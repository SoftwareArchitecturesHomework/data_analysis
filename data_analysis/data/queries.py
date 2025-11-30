from sqlalchemy import create_engine, text
import pandas as pd
from config.settings import settings

engine = create_engine(settings.database_url, future=True)

def fetch_view(name: str) -> pd.DataFrame:
    query = text(f"SELECT * FROM {name}")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def fetch_view_by_manager(name: str, manager_id: int) -> pd.DataFrame:
    query = text(f'SELECT * FROM {name} WHERE "{name}"."managerId" = :mid')
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"mid": manager_id})

def fetch_manager(manager_id: int):
    query = text(f'SELECT name FROM "workplanner"."User" WHERE id = :mid')
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"mid": manager_id})
    if not df.empty:
        return str(df.iloc[0, 0])
    return None

def fetch_all_manager_ids() -> list[int]:
    query = text('SELECT DISTINCT "ownerId" FROM "workplanner"."Project"')

    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        if df.empty:
            return []

        return df['ownerId'].astype(int).tolist()

    except Exception as e:
        print(f"Database error fetching manager IDs: {e}")
        return []

def get_project_employee_total_hours():
    return fetch_view("project_employee_total_hours")


def get_avg_completed_project_duration():
    return fetch_view("avg_completed_project_duration")


def get_project_duration_variance():
    return fetch_view("project_duration_variance")


def get_monthly_project_hours():
    return fetch_view("monthly_project_hours")

def get_project_employee_total_hours_by_manager(manager_id):
    return fetch_view_by_manager("project_employee_total_hours", manager_id)


def get_avg_completed_project_duration_hours_by_manager(manager_id):
    return fetch_view_by_manager("avg_completed_project_duration", manager_id)


def get_project_duration_variance_hours_by_manager(manager_id):
    return fetch_view_by_manager("project_duration_variance", manager_id)


def get_monthly_project_hours_hours_by_manager(manager_id):
    return fetch_view_by_manager("monthly_project_hours", manager_id)
