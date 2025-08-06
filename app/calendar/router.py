from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import pytz

from app.core.dependencies import get_db
from . import crud, schemas

router = APIRouter(tags=["Calendar"])
templates = Jinja2Templates(directory="templates")
WARSAW_TZ = pytz.timezone('Europe/Warsaw')

def convert_to_naive_warsaw(dt: datetime):
    """Konwertuje świadomą datę UTC na naiwną datę w strefie warszawskiej."""
    if dt.tzinfo is None: return dt # Jeśli już jest naiwna, nie rób nic
    return dt.astimezone(WARSAW_TZ).replace(tzinfo=None)

@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request, "page_title": "Kalendarz"})


@router.get("/api/calendar/events")
async def get_calendar_events(start: datetime, end: datetime, db: Session = Depends(get_db)):
    start_local = convert_to_naive_warsaw(start)
    end_local = convert_to_naive_warsaw(end)

    appointments = crud.get_appointments(db, start=start_local, end=end_local)

    events = []
    for app in appointments:
        class_names = []

        if app.start_time < datetime.now():
            class_names.append('event-past')
            if app.status == 'zaplanowana':
                class_names.append('event-overdue')

        event_title = f"{app.client.first_name} {app.client.last_name}"

        events.append({
            "id": app.id,
            "title": event_title,
            "start": app.start_time.isoformat(),
            "end": app.end_time.isoformat(),
            "color": app.service_type.category.color,
            "className": " ".join(class_names),
            "extendedProps": {
                "serviceName": app.service_type.name,
                "price": app.price,
                "description": app.description,
                "phoneNumber": app.client.phone_number,
                "serviceTypeId": app.service_type.id,
                "clientId": app.client.id
            }
        })
    return events

@router.post("/api/calendar/events", status_code=201)
async def create_event(appointment_data: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    appointment_data.start = convert_to_naive_warsaw(appointment_data.start)
    appointment_data.end = convert_to_naive_warsaw(appointment_data.end)

    if appointment_data.start < datetime.now():
        raise HTTPException(status_code=400, detail="Nie można tworzyć wizyt w przeszłości.")
    if crud.check_for_overlap(db, start_time=appointment_data.start, end_time=appointment_data.end):
        raise HTTPException(status_code=409, detail="Termin jest już zajęty przez inną wizytę.")

    db_appointment, new_client = crud.create_appointment(db, appointment_data)
    new_client_data = schemas.ClientInDB.from_orm(new_client) if new_client else None

    return {
        "success": True,
        "appointment": {"id": db_appointment.id},
        "new_client": new_client_data
    }

@router.put("/api/calendar/events/{event_id}")
async def update_event(event_id: int, update_data: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    # Konwertujemy daty na początku, jeśli zostały przesłane
    if update_data.start:
        update_data.start = convert_to_naive_warsaw(update_data.start)
    if update_data.end:
        update_data.end = convert_to_naive_warsaw(update_data.end)

    # if update_data.start and update_data.start < datetime.now():
    #     raise HTTPException(status_code=400, detail="Nie można przenosić wizyt w przeszłość.")

    if update_data.start and update_data.end and crud.check_for_overlap(db, start_time=update_data.start,
                                                                        end_time=update_data.end,
                                                                        appointment_id=event_id):
        raise HTTPException(status_code=409, detail="Ten termin jest już zajęty.")

    # Logika edycji (bez zmian)
    if update_data.service_type_id is not None:
        updated = crud.update_appointment(db, appointment_id=event_id, appointment_data=update_data)
    else:
        updated = crud.update_appointment_time(db, appointment_id=event_id, start=update_data.start,
                                               end=update_data.end)

    if not updated:
        raise HTTPException(status_code=404, detail="Wizyta nie znaleziona")
    return updated

@router.post("/api/calendar/events/{event_id}/complete")
async def complete_event(event_id: int, db: Session = Depends(get_db)):
    """Oznacza wizytę jako wykonaną."""
    return crud.mark_appointment_as_completed(db, appointment_id=event_id)

@router.post("/api/calendar/events/{event_id}/cancel")
async def cancel_event(event_id: int, reason: str = Form(...), db: Session = Depends(get_db)):
    """Oznacza wizytę jako anulowaną z podanym powodem."""
    cancelled_appointment = crud.cancel_appointment(db, appointment_id=event_id, reason=reason)
    if not cancelled_appointment:
        raise HTTPException(status_code=404, detail="Wizyta nie znaleziona")
    return {"success": True, "message": "Wizyta została anulowana."}