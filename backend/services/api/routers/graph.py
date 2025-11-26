from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from backend.services.api.dependencies import DatabaseDep, CurrentUserDep
from backend.shared.models import Company

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{company_id}")
async def get_company_graph(
    company_id: int,
    db: DatabaseDep,
    current_user: CurrentUserDep,  # Require auth
    depth: int = 1
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get network graph data for a company.
    Nodes: Companies and Officers.
    Edges: Relationships (e.g. CEO, Shareholder).
    """
    
    # 1. Fetch the seed company
    company_res = db.table("companies").select("*").eq("id", company_id).execute()
    if not company_res.data:
        raise HTTPException(status_code=404, detail="Company not found")
    
    seed_company = company_res.data[0]
    
    nodes = []
    edges = []
    
    # Add seed node
    nodes.append({
        "data": {
            "id": f"c_{seed_company['id']}",
            "label": seed_company['name'],
            "type": "company",
            "color": "#2563eb" # Blue
        }
    })
    
    # 2. Fetch officers
    officers_res = db.table("company_officers").select("*").eq("company_id", company_id).execute()
    officers = officers_res.data or []
    
    for officer in officers:
        officer_id = f"o_{officer['id']}"
        officer_name = officer.get('full_name') or f"{officer.get('first_name', '')} {officer.get('last_name', '')}".strip()
        role = officer.get('role', 'Officer')
        
        # Add officer node
        nodes.append({
            "data": {
                "id": officer_id,
                "label": officer_name,
                "type": "person",
                "color": "#16a34a" # Green
            }
        })
        
        # Add edge from company to officer (or vice versa depending on role, but for now undirected/simple)
        edges.append({
            "data": {
                "source": f"c_{seed_company['id']}",
                "target": officer_id,
                "label": role,
                "edge_type": "management",
            }
        })
        
        # Depth 2: Find other companies this officer is part of
        if depth > 1 and officer_name:
            # Find other officers with same name
            # Note: This is a fuzzy match and might link different people with same name.
            # In a real app, we'd need a unique person ID.
            related_res = db.table("company_officers").select("company_id, role").eq("full_name", officer_name).neq("company_id", company_id).limit(5).execute()
            
            for rel in related_res.data or []:
                rel_company_id = rel['company_id']
                rel_role = rel.get('role', 'Officer')
                
                # Fetch that company name
                rel_comp_res = db.table("companies").select("name").eq("id", rel_company_id).execute()
                if rel_comp_res.data:
                    rel_comp_name = rel_comp_res.data[0]['name']
                    
                    # Add related company node
                    rel_node_id = f"c_{rel_company_id}"
                    
                    # Check if node already exists
                    if not any(n['data']['id'] == rel_node_id for n in nodes):
                        nodes.append({
                            "data": {
                                "id": rel_node_id,
                                "label": rel_comp_name,
                                "type": "company",
                                "color": "#2563eb"
                            }
                        })
                    
                    # Add edge from officer to related company
                    edges.append({
                        "data": {
                            "source": officer_id,
                            "target": rel_node_id,
                            "label": rel_role,
                            "edge_type": "affiliation",
                        }
                    })

    return {
        "elements": nodes + edges
    }
