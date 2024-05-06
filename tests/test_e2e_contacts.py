def test_get_contacts(client, get_token):
    tocken = get_token
    headers = {"Authorization": f"Bearer {tocken}"}
    response = client.get("api/contacts", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2


def test_get_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    contact_id = 1
    response = client.get(f"api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "phone" in data
    assert "birthday" in data


def test_get_wrong_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    contact_id = 3
    response = client.get(f"api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 404, response.text


def test_update_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "name": "Updated Name",
        "phone": "0674444445",
        "birthday": "1990-01-01",
    }
    response = client.put("api/contacts/", json=update_data, headers=headers)
    assert response.status_code == 200, response.text
    updated_contact = response.json()
    assert updated_contact["name"] == update_data["name"]
    assert updated_contact["phone"] == update_data["phone"]
    assert updated_contact["birthday"] == update_data["birthday"]


def test_search_contact(client, get_token):
    tocken = get_token
    headers = {"Authorization": f"Bearer {tocken}"}
    field_search = "067444"
    response = client.get(f"api/contacts/search/{field_search}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2


def test_delete_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("api/contacts/", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "phone" in data
    assert "birthday" in data
