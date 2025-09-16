import requests

access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjI2NTdmYTdjZjBhYzg4NjlmMmJjNWEzNzEzMDEwYTAzYjYwMWY4ODRhMDE2NzczMTcwMzhmN2Q1YmM0MTkxMzBhOTc0NDNjZmY3MDU3YWIwIn0.eyJhdWQiOiJjNjA2NWI2Ny00Zjc0LTRkZDEtODUyYi1kODEzNTkyMjRjODYiLCJqdGkiOiIyNjU3ZmE3Y2YwYWM4ODY5ZjJiYzVhMzcxMzAxMGEwM2I2MDFmODg0YTAxNjc3MzE3MDM4ZjdkNWJjNDE5MTMwYTk3NDQzY2ZmNzA1N2FiMCIsImlhdCI6MTc1MTEzODUyNywibmJmIjoxNzUxMTM4NTI3LCJleHAiOjE3NjcxMzkyMDAsInN1YiI6IjMzMDY0NDIiLCJncmFudF90eXBlIjoiIiwiYWNjb3VudF9pZCI6MjUwMzE2NzcsImJhc2VfZG9tYWluIjoiYW1vY3JtLnJ1IiwidmVyc2lvbiI6Miwic2NvcGVzIjpbImNybSIsImZpbGVzIiwiZmlsZXNfZGVsZXRlIiwibm90aWZpY2F0aW9ucyIsInB1c2hfbm90aWZpY2F0aW9ucyJdLCJoYXNoX3V1aWQiOiJiMWFjMjlhMS05OGY5LTQ4ZGEtOTRiZS1jN2IxNDFhM2FiYTUiLCJhcGlfZG9tYWluIjoiYXBpLWIuYW1vY3JtLnJ1In0.o7RpPR9A4ENLMNdz3pCTlOx4OC6P5C-u1taAWrV7v-uctxa-_qIiMocFMTO24-N_d9JrK2LqbAGGeRq6fAmVrQ_JkOGo4vr9VGKYaT7pe_sfKa4ba99TiHsCLUGqpZc21Gp6G8LZO4PPkHbC79klNYpEnq3J4ozr-vfjXkk9FTF_8NrW2QCU7RTohC2SQtnZ6cxVZ7k5JljKLRa6J9rFTvo5yRNLLdHyh3GuO80KOTBci08meyi_9zpzhk1YXnEBpvJoHLhDc6sQXHejE-2eJUL_sosZko9R6us2jBBgsxqB5qlCV6QmvLl3TEyLHYWIzNwWz6hhE20NpwzcXGhELw'
url = 'https://tnamo.amocrm.ru/api/v4/leads'
headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    leads = response.json()
    print("Лиды успешно получены:")
    for lead in leads['_embedded']['leads']:
        print(f"ID лида: {lead['id']}, Название: {lead['name']}")
else:
    print(f"Ошибка при получении данных: {response.status_code}, {response.text}")