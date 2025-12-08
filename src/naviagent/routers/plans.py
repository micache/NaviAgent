from fastapi import APIRouter, Depends, HTTPException, status
from naviagent.core.auth import authenticate_user
from naviagent.core.database import get_supabase_service
from naviagent.models.models import PlanModel
from naviagent.schemas.models import CreatePlanRequest, Plan
from typing import Any, Dict, List
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/plans", tags=["plans"])

# TEMPORARY: Use service role key to bypass RLS until policies are configured
USE_SERVICE_ROLE = os.getenv("USE_SERVICE_ROLE_FOR_PLANS", "true").lower() == "true"


@router.post("/", response_model=Plan, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_request: CreatePlanRequest,
    current_user: Dict[str, Any] = Depends(authenticate_user),
):
    """
    Tạo plan mới và lưu vào database.
    
    - Lưu thông tin travel plan vào bảng plans
    - Upload HTML guidebook lên Supabase Storage (nếu có)
    - Trả về plan đã tạo với guidebook URL
    """
    print(f"📥 Received create_plan request from user: {current_user['user_id']}")
    print(f"📋 Plan data: destination={plan_request.destination}, duration={plan_request.duration}")
    
    # TEMPORARY: Use service role to bypass RLS until policies are setup
    # TODO: Remove this and use authenticated client after configuring RLS policies
    if USE_SERVICE_ROLE:
        print("⚠️ Using service role key (bypasses RLS) - configure RLS policies for production!")
        supabase = get_supabase_service()
    else:
        print("✅ Using authenticated client with RLS")
        supabase = current_user["supabase"]
    
    user_id = current_user["user_id"]
    
    try:
        # Generate plan ID
        plan_id = str(uuid.uuid4())
        
        # Prepare plan data
        plan_data = {
            "id": plan_id,
            "user_id": user_id,
            "destination": plan_request.destination,
            "departure": plan_request.departure,
            "start_date": plan_request.start_date.isoformat(),
            "duration": plan_request.duration,
            "number_of_travelers": plan_request.number_of_travelers,
            "budget": plan_request.budget,
            "travel_style": plan_request.travel_style,
            "notes": plan_request.notes,
            "guidebook": None,  # Will update after upload
        }
        
        # Upload guidebook HTML to Supabase Storage if provided
        if plan_request.guidebook:
            print(f"📚 Uploading guidebook to Storage (size: {len(plan_request.guidebook)} chars)")
            try:
                # Storage bucket name
                bucket_name = "guidebooks"
                
                # Create file path: guidebooks/{user_id}/{plan_id}.html
                file_path = f"{user_id}/{plan_id}.html"
                
                print(f"📁 Storage path: {bucket_name}/{file_path}")
                
                # Upload HTML content as bytes
                html_bytes = plan_request.guidebook.encode('utf-8')
                
                # Upload to Supabase Storage
                storage_response = supabase.storage.from_(bucket_name).upload(
                    file_path,
                    html_bytes,
                    {
                        "content-type": "text/html; charset=utf-8",
                        "upsert": "true"  # Overwrite if exists
                    }
                )
                
                # Get public URL
                public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                plan_data["guidebook"] = public_url
                
                print(f"✅ Uploaded guidebook to Storage: {public_url}")
                
            except Exception as storage_error:
                print(f"⚠️ Storage upload failed: {storage_error}")
                print(f"   Error type: {type(storage_error).__name__}")
                # Continue without guidebook URL
        else:
            print("ℹ️ No guidebook content provided")
        
        # Insert plan into database
        print(f"💾 Inserting plan into database table: {PlanModel.__tablename__}")
        result = supabase.table(PlanModel.__tablename__).insert(plan_data).execute()
        
        print(f"📊 Database response: {result}")
        
        if not result.data:
            print("❌ No data returned from database insert")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create plan in database"
            )
        
        created_plan = result.data[0]
        print(f"✅ Plan created successfully with ID: {created_plan['id']}")
        
        return Plan(
            id=created_plan["id"],
            user_id=created_plan["user_id"],
            destination=created_plan["destination"],
            departure=created_plan["departure"],
            start_date=datetime.fromisoformat(created_plan["start_date"]).date(),
            duration=created_plan["duration"],
            number_of_travelers=created_plan["number_of_travelers"],
            budget=created_plan["budget"],
            travel_style=created_plan["travel_style"],
            notes=created_plan["notes"],
            guidebook=created_plan["guidebook"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating plan: {str(e)}"
        )


@router.get("/", response_model=List[Plan])
async def get_user_plans(
    current_user: Dict[str, Any] = Depends(authenticate_user),
):
    """
    Lấy danh sách tất cả plans của user hiện tại.
    """
    if USE_SERVICE_ROLE:
        supabase = get_supabase_service()
    else:
        supabase = current_user["supabase"]
    user_id = current_user["user_id"]
    
    try:
        result = (
            supabase.table(PlanModel.__tablename__)
            .select("*")
            .eq("user_id", user_id)
            .order("start_date", desc=True)
            .execute()
        )
        
        plans = []
        for plan_data in result.data:
            plans.append(Plan(
                id=plan_data["id"],
                user_id=plan_data["user_id"],
                destination=plan_data["destination"],
                departure=plan_data["departure"],
                start_date=datetime.fromisoformat(plan_data["start_date"]).date(),
                duration=plan_data["duration"],
                number_of_travelers=plan_data["number_of_travelers"],
                budget=plan_data["budget"],
                travel_style=plan_data["travel_style"],
                notes=plan_data["notes"],
                guidebook=plan_data["guidebook"],
            ))
        
        return plans
        
    except Exception as e:
        print(f"❌ Error fetching plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching plans: {str(e)}"
        )


@router.get("/{plan_id}", response_model=Plan)
async def get_plan_by_id(
    plan_id: str,
    current_user: Dict[str, Any] = Depends(authenticate_user),
):
    """
    Lấy chi tiết một plan theo ID.
    """
    if USE_SERVICE_ROLE:
        supabase = get_supabase_service()
    else:
        supabase = current_user["supabase"]
    user_id = current_user["user_id"]
    
    try:
        result = (
            supabase.table(PlanModel.__tablename__)
            .select("*")
            .eq("id", plan_id)
            .eq("user_id", user_id)
            .execute()
        )
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        plan_data = result.data[0]
        
        return Plan(
            id=plan_data["id"],
            user_id=plan_data["user_id"],
            destination=plan_data["destination"],
            departure=plan_data["departure"],
            start_date=datetime.fromisoformat(plan_data["start_date"]).date(),
            duration=plan_data["duration"],
            number_of_travelers=plan_data["number_of_travelers"],
            budget=plan_data["budget"],
            travel_style=plan_data["travel_style"],
            notes=plan_data["notes"],
            guidebook=plan_data["guidebook"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching plan: {str(e)}"
        )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    current_user: Dict[str, Any] = Depends(authenticate_user),
):
    """
    Xóa một plan (và guidebook HTML trong Storage nếu có).
    """
    if USE_SERVICE_ROLE:
        supabase = get_supabase_service()
    else:
        supabase = current_user["supabase"]
    user_id = current_user["user_id"]
    
    try:
        # Get plan first to check ownership and get guidebook path
        result = (
            supabase.table(PlanModel.__tablename__)
            .select("*")
            .eq("id", plan_id)
            .eq("user_id", user_id)
            .execute()
        )
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Delete guidebook from Storage if exists
        try:
            file_path = f"{user_id}/{plan_id}.html"
            supabase.storage.from_("guidebooks").remove([file_path])
            print(f"✅ Deleted guidebook from Storage: {file_path}")
        except Exception as storage_error:
            print(f"⚠️ Storage delete failed: {storage_error}")
            # Continue with plan deletion
        
        # Delete plan from database
        supabase.table(PlanModel.__tablename__).delete().eq("id", plan_id).eq("user_id", user_id).execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting plan: {str(e)}"
        )

