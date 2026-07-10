import logging
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import nulls_last
from models import User, ExtractedEvent
from services.gmail_service import fetch_new_emails
from services.gemini_service import process_unprocessed_emails
from services.sheets_service import sync_all_unsynced_events

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')


@dashboard_bp.route('/fetch/now', methods=['POST'])
@jwt_required()
def trigger_fetch_now():
    """
    Fetch new emails from Gmail AND immediately run AI extraction on them.
    Returns a combined result: {"fetch": {...}, "process": {...}}
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        fetch_result = fetch_new_emails(user)
        process_result = process_unprocessed_emails(user)

        return jsonify({
            "fetch": fetch_result,
            "process": process_result
        }), 200

    except Exception as e:
        logging.error(f"Error in /api/fetch/now: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to fetch/process emails", "details": str(e)}), 500


@dashboard_bp.route('/process/emails', methods=['POST'])
@jwt_required()
def trigger_process_emails():
    """
    Manually trigger AI extraction on all currently unprocessed emails.
    Returns: {"processed": N, "events_created": N, "batches": N}
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        result = process_unprocessed_emails(user)
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in /api/process/emails: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to process emails", "details": str(e)}), 500


@dashboard_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    """
    Fetch extracted events for the current user.
    Optional query params:
      - type:   filter by ExtractedEvent.type   (MEETING, EXAM, DEADLINE, INTERVIEW, REMINDER, OTHER)
      - status: filter by ExtractedEvent.status (PENDING, DONE, SNOOZED)
    Returns a JSON array ordered by date ascending (nulls last).
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        type_filter = request.args.get('type')
        status_filter = request.args.get('status')

        query = ExtractedEvent.query.filter_by(user_id=user.id)

        if type_filter:
            query = query.filter(ExtractedEvent.type == type_filter.upper())

        if status_filter:
            query = query.filter(ExtractedEvent.status == status_filter.upper())

        # Order by date ascending, nulls at the end
        events = query.order_by(nulls_last(ExtractedEvent.date.asc())).all()

        return jsonify([
            {
                "id": e.id,
                "title": e.title,
                "date": e.date.isoformat() if e.date else None,
                "time": e.time.strftime("%H:%M") if e.time else None,
                "type": e.type,
                "location": e.location,
                "description": e.description,
                "status": e.status,
            }
            for e in events
        ]), 200

    except Exception as e:
        logging.error(f"Error in /api/events: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to retrieve events", "details": str(e)}), 500


@dashboard_bp.route('/events/<int:event_id>/done', methods=['POST'])
@jwt_required()
def mark_event_done(event_id):
    """
    Mark an event as DONE.
    """
    try:
        user_id = get_jwt_identity()
        event = ExtractedEvent.query.get(event_id)
        
        if not event:
            return jsonify({"error": "Event not found"}), 404
            
        if event.user_id != int(user_id):
            return jsonify({"error": "Permission denied"}), 403
            
        event.status = "DONE"
        from extensions import db
        db.session.commit()
        
        return jsonify({
            "id": event.id,
            "title": event.title,
            "date": event.date.isoformat() if event.date else None,
            "time": event.time.strftime("%H:%M") if event.time else None,
            "type": event.type,
            "location": event.location,
            "description": event.description,
            "status": event.status
        }), 200
        
    except Exception as e:
        logging.error(f"Error marking event as done: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to update event", "details": str(e)}), 500


@dashboard_bp.route('/events/<int:event_id>/snooze', methods=['POST'])
@jwt_required()
def snooze_event(event_id):
    """
    Mark an event as SNOOZED.
    """
    try:
        user_id = get_jwt_identity()
        event = ExtractedEvent.query.get(event_id)
        
        if not event:
            return jsonify({"error": "Event not found"}), 404
            
        if event.user_id != int(user_id):
            return jsonify({"error": "Permission denied"}), 403
            
        event.status = "SNOOZED"
        from extensions import db
        db.session.commit()
        
        return jsonify({
            "id": event.id,
            "title": event.title,
            "date": event.date.isoformat() if event.date else None,
            "time": event.time.strftime("%H:%M") if event.time else None,
            "type": event.type,
            "location": event.location,
            "description": event.description,
            "status": event.status
        }), 200
        
    except Exception as e:
        logging.error(f"Error snoozing event: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to update event", "details": str(e)}), 500


@dashboard_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@jwt_required()
def delete_event(event_id):
    """
    Delete an event entirely.
    """
    try:
        user_id = get_jwt_identity()
        event = ExtractedEvent.query.get(event_id)
        
        if not event:
            return jsonify({"error": "Event not found"}), 404
            
        if event.user_id != int(user_id):
            return jsonify({"error": "Permission denied"}), 403
            
        from extensions import db
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            "deleted": True,
            "id": event_id
        }), 200
        
    except Exception as e:
        logging.error(f"Error deleting event: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to delete event", "details": str(e)}), 500


@dashboard_bp.route('/export/pdf', methods=['GET'])
@jwt_required()
def export_pdf():
    """
    Generate and download a PDF containing all extracted events for the current user.
    """
    import io
    from datetime import datetime
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fetch events ordered by date ascending (nulls last)
        events = ExtractedEvent.query.filter_by(user_id=user.id)\
            .order_by(nulls_last(ExtractedEvent.date.asc())).all()

        # Set up PDF document in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Define clean, professional custom styles
        title_style = ParagraphStyle(
            'PDFTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f0f1b'),
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'PDFSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=20
        )
        
        header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white
        )
        
        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#1e293b')
        )

        story = []

        # Add Title & Subtitle
        story.append(Paragraph("SmartInbox — My Events", title_style))
        current_date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Generated on {current_date_str} | Active Account: {user.email}", subtitle_style))
        story.append(Spacer(1, 10))

        # Table data columns: Title | Type | Date | Time | Location | Status
        table_data = [[
            Paragraph("Title", header_style),
            Paragraph("Type", header_style),
            Paragraph("Date", header_style),
            Paragraph("Time", header_style),
            Paragraph("Location", header_style),
            Paragraph("Status", header_style),
        ]]

        for e in events:
            date_val = e.date.isoformat() if e.date else "—"
            time_val = e.time.strftime("%H:%M") if e.time else "—"
            loc_val = e.location if e.location else "—"
            table_data.append([
                Paragraph(e.title or "Untitled", cell_style),
                Paragraph(e.type or "OTHER", cell_style),
                Paragraph(date_val, cell_style),
                Paragraph(time_val, cell_style),
                Paragraph(loc_val, cell_style),
                Paragraph(e.status or "PENDING", cell_style),
            ])

        # Printable width = letter width (612) - leftMargin (36) - rightMargin (36) = 540 points
        col_widths = [160, 70, 70, 50, 100, 90]
        event_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Style table cleanly with professional gridlines
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a35')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(event_table)

        # Build Document
        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name='smartinbox_events.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        logging.error(f"Error exporting events PDF: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to generate PDF", "details": str(e)}), 500


@dashboard_bp.route('/sheet/sync', methods=['POST'])
@jwt_required()
def trigger_sheet_sync():
    """
    Manually trigger a Google Sheets sync for the current user.
    Calls sync_all_unsynced_events and returns the count of newly synced events.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        result = sync_all_unsynced_events(user)
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in /api/sheet/sync: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to sync to Google Sheets", "details": str(e)}), 500


@dashboard_bp.route('/sheet/link', methods=['GET'])
@jwt_required()
def get_sheet_link():
    """
    Returns the Google Sheets URL linked to the current user, or null if not yet linked.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        sheet_id = user.profile.linked_sheet_id if user.profile else None
        sheet_url = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
            if sheet_id else None
        )
        return jsonify({"sheet_url": sheet_url}), 200

    except Exception as e:
        logging.error(f"Error in /api/sheet/link: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to get sheet link", "details": str(e)}), 500
