from app.dto.catalog_dto import UniformDTO, UniformUpdateRequest
from app.services.uniform_service import UniformService
from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Union, Optional, Dict, Any, List
router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])

_uniform_service = UniformService()

# ADD UNIFORM
@router.post("/add-uniform")
def create_uniform(uniform: UniformDTO):
    return _uniform_service.create_new_uniform(uniform)

# UPDATE UNIFORM
@router.put("/update-uniform/{product_id}")
def update_uniform(product_id: str, request: UniformUpdateRequest):
    return _uniform_service.update_uniform(product_id, request.updates, request.size_updates)

# List all uniforms (no filter)
@router.get("/list-uniforms")
def list_all_uniforms():
    return _uniform_service.list_uniforms()

# Filter uniforms by type
@router.get("/filter-uniform")
def list_rtu_uniforms(uniform_type: str = None):
    return _uniform_service.filter_uniforms(uniform_type)

# DELETE (SOFT DELETE) UNIFORM
@router.delete("/delete-uniform/{product_id}")
def delete_uniform(product_id: str):
    return _uniform_service.delete_uniform(product_id)