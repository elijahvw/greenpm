"""
Messaging System API
Handles in-app messaging between tenants, landlords, and admin
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from src.core.database import get_db
from src.dependencies.auth import get_current_user, require_roles
from src.models.user import User
from src.models.message import Message, MessageThread
from src.models.property import Property
from src.models.lease import Lease
from src.schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageList,
    MessageThreadCreate,
    MessageThreadResponse,
    MessageThreadList,
    MessageStatus
)
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/threads", response_model=MessageThreadResponse)
async def create_message_thread(
    thread: MessageThreadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new message thread"""
    
    # Verify participants exist
    participants = db.query(User).filter(User.id.in_(thread.participant_ids)).all()
    if len(participants) != len(thread.participant_ids):
        raise HTTPException(status_code=404, detail="One or more participants not found")
    
    # Add current user to participants if not already included
    if current_user.id not in thread.participant_ids:
        thread.participant_ids.append(current_user.id)
    
    # Create message thread
    db_thread = MessageThread(
        **thread.dict(),
        created_by=current_user.id,
        last_message_at=datetime.utcnow()
    )
    
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    
    # Send notification to participants
    notification_service = NotificationService()
    for participant_id in thread.participant_ids:
        if participant_id != current_user.id:
            background_tasks.add_task(
                notification_service.send_message_notification,
                participant_id,
                current_user,
                db_thread,
                "thread_created"
            )
    
    return db_thread

@router.get("/threads", response_model=MessageThreadList)
async def get_message_threads(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get message threads for current user"""
    
    query = db.query(MessageThread).filter(
        MessageThread.participant_ids.contains([current_user.id])
    )
    
    if unread_only:
        # Get threads with unread messages
        unread_threads = db.query(Message.thread_id).filter(
            and_(
                Message.sender_id != current_user.id,
                Message.read_by.op('?')(current_user.id) == False
            )
        ).distinct()
        query = query.filter(MessageThread.id.in_(unread_threads))
    
    # Order by last message time
    query = query.order_by(desc(MessageThread.last_message_at))
    
    total = query.count()
    threads = query.offset(skip).limit(limit).all()
    
    return MessageThreadList(
        threads=threads,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/threads/{thread_id}", response_model=MessageThreadResponse)
async def get_message_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific message thread"""
    
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    # Check if user is participant
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return thread

@router.post("/", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a new message"""
    
    # Verify thread exists and user is participant
    thread = db.query(MessageThread).filter(MessageThread.id == message.thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create message
    db_message = Message(
        **message.dict(),
        sender_id=current_user.id,
        read_by={current_user.id: datetime.utcnow().isoformat()}
    )
    
    db.add(db_message)
    
    # Update thread last message time
    thread.last_message_at = datetime.utcnow()
    thread.last_message_id = db_message.id
    
    db.commit()
    db.refresh(db_message)
    
    # Send notifications to other participants
    notification_service = NotificationService()
    for participant_id in thread.participant_ids:
        if participant_id != current_user.id:
            background_tasks.add_task(
                notification_service.send_message_notification,
                participant_id,
                current_user,
                db_message,
                "message_received"
            )
    
    return db_message

@router.get("/", response_model=MessageList)
async def get_messages(
    thread_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages in a thread"""
    
    # Verify thread exists and user is participant
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get messages
    query = db.query(Message).filter(Message.thread_id == thread_id)
    query = query.order_by(desc(Message.created_at))
    
    total = query.count()
    messages = query.offset(skip).limit(limit).all()
    
    return MessageList(
        messages=messages,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific message"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user is participant in thread
    thread = db.query(MessageThread).filter(MessageThread.id == message.thread_id).first()
    if not thread or current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return message

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_update: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update message (sender only)"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Only sender can update message
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update allowed fields
    if message_update.content is not None:
        message.content = message_update.content
        message.edited_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    return message

@router.post("/{message_id}/read")
async def mark_message_read(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark message as read"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user is participant in thread
    thread = db.query(MessageThread).filter(MessageThread.id == message.thread_id).first()
    if not thread or current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mark as read
    if not message.read_by:
        message.read_by = {}
    
    message.read_by[current_user.id] = datetime.utcnow().isoformat()
    message.read_by = message.read_by  # Trigger SQLAlchemy update
    
    db.commit()
    
    return {"message": "Message marked as read"}

@router.post("/threads/{thread_id}/mark-read")
async def mark_thread_read(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all messages in thread as read"""
    
    # Verify thread exists and user is participant
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mark all messages in thread as read
    messages = db.query(Message).filter(
        and_(
            Message.thread_id == thread_id,
            Message.sender_id != current_user.id
        )
    ).all()
    
    current_time = datetime.utcnow().isoformat()
    
    for message in messages:
        if not message.read_by:
            message.read_by = {}
        message.read_by[current_user.id] = current_time
        message.read_by = message.read_by  # Trigger SQLAlchemy update
    
    db.commit()
    
    return {"message": f"Marked {len(messages)} messages as read"}

@router.get("/threads/{thread_id}/participants", response_model=List[dict])
async def get_thread_participants(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get participants in message thread"""
    
    # Verify thread exists and user is participant
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get participant details
    participants = db.query(User).filter(User.id.in_(thread.participant_ids)).all()
    
    return [
        {
            "id": p.id,
            "email": p.email,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "role": p.role
        }
        for p in participants
    ]

@router.post("/threads/{thread_id}/add-participant")
async def add_thread_participant(
    thread_id: str,
    participant_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Add participant to message thread"""
    
    # Verify thread exists and user is participant
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify new participant exists
    participant = db.query(User).filter(User.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Add participant if not already in thread
    if participant_id not in thread.participant_ids:
        thread.participant_ids.append(participant_id)
        thread.participant_ids = thread.participant_ids  # Trigger SQLAlchemy update
        
        db.commit()
        
        # Send notification
        notification_service = NotificationService()
        background_tasks.add_task(
            notification_service.send_message_notification,
            participant_id,
            current_user,
            thread,
            "added_to_thread"
        )
    
    return {"message": "Participant added to thread"}

@router.delete("/threads/{thread_id}/participants/{participant_id}")
async def remove_thread_participant(
    thread_id: str,
    participant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Remove participant from message thread"""
    
    # Verify thread exists and user is participant
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    if current_user.id not in thread.participant_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Remove participant
    if participant_id in thread.participant_ids:
        thread.participant_ids.remove(participant_id)
        thread.participant_ids = thread.participant_ids  # Trigger SQLAlchemy update
        
        db.commit()
    
    return {"message": "Participant removed from thread"}

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread messages"""
    
    # Get threads user participates in
    user_threads = db.query(MessageThread.id).filter(
        MessageThread.participant_ids.contains([current_user.id])
    ).subquery()
    
    # Count unread messages
    unread_count = db.query(Message).filter(
        and_(
            Message.thread_id.in_(user_threads),
            Message.sender_id != current_user.id,
            or_(
                Message.read_by.is_(None),
                Message.read_by.op('?')(current_user.id) == False
            )
        )
    ).count()
    
    return {"unread_count": unread_count}

@router.post("/quick-message")
async def send_quick_message(
    recipient_id: str,
    subject: str,
    content: str,
    background_tasks: BackgroundTasks,
    property_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a quick message (creates thread automatically)"""
    
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Check if there's an existing thread between these users
    existing_thread = db.query(MessageThread).filter(
        and_(
            MessageThread.participant_ids.contains([current_user.id]),
            MessageThread.participant_ids.contains([recipient_id])
        )
    ).first()
    
    if existing_thread:
        thread_id = existing_thread.id
    else:
        # Create new thread
        thread_data = {
            "subject": subject,
            "participant_ids": [current_user.id, recipient_id],
            "property_id": property_id
        }
        
        new_thread = MessageThread(
            **thread_data,
            created_by=current_user.id,
            last_message_at=datetime.utcnow()
        )
        
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        thread_id = new_thread.id
    
    # Send message
    message_data = {
        "thread_id": thread_id,
        "content": content
    }
    
    db_message = Message(
        **message_data,
        sender_id=current_user.id,
        read_by={current_user.id: datetime.utcnow().isoformat()}
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Send notification
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_message_notification,
        recipient_id,
        current_user,
        db_message,
        "message_received"
    )
    
    return {"message": "Quick message sent successfully", "thread_id": thread_id}

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete message (sender only or admin)"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check permissions
    if current_user.role != "admin" and message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully"}

@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Delete message thread (admin only)"""
    
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Message thread not found")
    
    # Delete all messages in thread
    db.query(Message).filter(Message.thread_id == thread_id).delete()
    
    # Delete thread
    db.delete(thread)
    db.commit()
    
    return {"message": "Message thread deleted successfully"}