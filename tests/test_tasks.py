from fastapi import status
import pytest

@pytest.mark.asyncio
async def tets_create_task(client):
    
    task_data = {
        "title": "Купить молоко",
        "description": "В магазине у дома",
        "is_completed": False
    }
    
    response = client.post('/tasks/', json=task_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['title'] == task_data['title']
    assert 'id' in data
    assert 'created_at' in data

@pytest.mark.asyncio
async def test_get_empty_task(client):
    
    response = client.get('/tasks/')
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
    
@pytest.mark.asyncio    
async def test_get_tasks_with_data(client):
    
    task1 = {"title": "Задача 1", "description": "Описание 1"}
    task2 = {"title": "Задача 2", "description": "Описание 2"}
    
    client.post('/tasks', json=task1)
    client.post('/tasks', json=task2)
    
    response = client.get('/tasks')
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == task1['title']
    assert data[1]['title'] == task2['title']
    
@pytest.mark.asyncio    
async def test_get_task_by_id(client):
    
    task = {"title": "Тестовая задача"}
    create_resp = client.post('/tasks/', json=task)
    task_id = create_resp.json()['id']
    
    response = client.get(f'/tasks/{task_id}')
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == task_id
    assert data['title'] == task['title']
    
@pytest.mark.asyncio    
async def test_get_task_not_found(client):
    
    response = client.get('/tasks/9999')
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'не найдена' in response.json()['detail']
    
@pytest.mark.asyncio    
async def test_update_task(client):

    create_resp = client.post("/tasks/", json={"title": "Старый заголовок"})
    task_id = create_resp.json()["id"]
    update_data = {"title": "Новый заголовок", "description": "Новое описание", "is_completed": True}

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
    