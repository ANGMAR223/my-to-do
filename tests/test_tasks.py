from fastapi import status
import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_create_task(client):

    task_data = {
        "title": "Купить молоко",
        "description": "В магазине у дома",
        "is_completed": False,
    }

    response = client.post("/tasks/", json=task_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == task_data["title"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_empty_task(client):

    response = client.get("/tasks/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_tasks_with_data(client):
    task1 = {"title": "Задача 1", "description": "Описание 1"}
    task2 = {"title": "Задача 2", "description": "Описание 2"}

    client.post("/tasks/", json=task1)
    client.post("/tasks/", json=task2)

    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    titles = {task["title"] for task in data}
    assert titles == {task1["title"], task2["title"]}


@pytest.mark.asyncio
async def test_get_task_by_id(client):

    task = {"title": "Тестовая задача"}
    create_resp = client.post("/tasks/", json=task)
    task_id = create_resp.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == task["title"]


@pytest.mark.asyncio
async def test_get_task_not_found(client):

    response = client.get("/tasks/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "не найдена" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_task(client):

    create_resp = client.post("/tasks/", json={"title": "Старый заголовок"})
    task_id = create_resp.json()["id"]
    update_data = {
        "title": "Новый заголовок",
        "description": "Новое описание",
        "is_completed": True,
    }

    response = client.put(f"/tasks/{task_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["is_completed"] == update_data["is_completed"]


@pytest.mark.asyncio
async def test_update_task_not_found(client):
    update_data = {"title": "Неважно", "description": "Неважно", "is_completed": False}
    response = client.put("/tasks/9999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_task(client):

    create_resp = client.post("/tasks/", json={"title": "Удаляемая задача"})
    task_id = create_resp.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert "task_delete" in data

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_task_not_found(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_task_with_deadline_and_priority(client):
    task_data = {
        "title": "Важная задача",
        "description": "Сделать до дедлайна",
        "deadline": "2026-12-31",
        "priority": 3,
    }

    response = client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["deadline"] == task_data["deadline"]
    assert data["priority"] == task_data["priority"]


@pytest.mark.asyncio
async def test_create_task_with_past_deadline_fails(client):
    task_data = {"title": "Задача с прошлым дедлайном", "deadline": "2000-01-01"}

    response = client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Дедлайн не может быть в прошлом" in response.text


@pytest.mark.asyncio
async def test_get_today_tasks(client):
    today = date.today().isoformat()

    client.post("/tasks/", json={"title": "Сегодня", "deadline": today})

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    client.post("/tasks/", json={"title": "Завтра", "deadline": tomorrow})

    client.post("/tasks/", json={"title": "Без дедлайна"})

    response = client.get("/tasks/today")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Сегодня"


@pytest.mark.asyncio
async def test_get_upcoming_tasks(client):
    today = date.today()
    day3 = (today + timedelta(days=3)).isoformat()
    day10 = (today + timedelta(days=10)).isoformat()

    client.post("/tasks/", json={"title": "В диапазоне", "deadline": day3})
    client.post("/tasks/", json={"title": "Вне диапазона", "deadline": day10})

    response = client.get("/tasks/upcoming?days=7")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "В диапазоне"


@pytest.mark.asyncio
async def test_get_overdue_tasks(client):
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)

    resp = client.post("/tasks/", json={"title": "Просрочено", "deadline": tomorrow.isoformat()})
    assert resp.status_code == status.HTTP_201_CREATED
    task_id = resp.json()["id"]

    update_data = {
        "title": "Просрочено",
        "descriprion": "Проверка просроченой задачи",
        "is_completed": False,
        "deadline": yesterday.isoformat(),
        "priority": 2,
    }
    put_resp = client.put(f"/tasks/{task_id}", json=update_data)
    assert put_resp.status_code == status.HTTP_200_OK

    client.post("/tasks/", json={"title": "Ещё не просрочено", "deadline": tomorrow.isoformat()})

    response = client.get("/tasks/overdue")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Просрочено"


@pytest.mark.asyncio
async def test_sort_tasks_by_priority(client):
    client.post("/tasks/", json={"title": "Низкий", "priority": 1})
    client.post("/tasks/", json={"title": "Высокий", "priority": 3})
    client.post("/tasks/", json={"title": "Средний", "priority": 2})

    response = client.get("/tasks/?sort_by=priority")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["priority"] == 3
    assert data[1]["priority"] == 2
    assert data[2]["priority"] == 1
