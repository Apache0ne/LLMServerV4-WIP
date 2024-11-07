import pytest
from services.base_client import ServiceClient
from services.groq_client import GroqClient
from services.ollama_client import OllamaClient
from services.cerebras_client import CerebrasClient

@pytest.fixture
def mock_config():
    return {
        'api_key': 'test_key',
        'host': 'localhost',
        'port': 11434
    }

def test_service_client_abstract():
    with pytest.raises(TypeError):
        ServiceClient({})

@pytest.mark.asyncio
async def test_groq_client(mock_config, mocker):
    mocker.patch('groq.AsyncGroq')
    client = GroqClient(mock_config)
    assert client.client is not None

    mocker.patch.object(client.client.chat.completions, 'create', return_value=mocker.Mock(choices=[mocker.Mock(message=mocker.Mock(content='Test response'))]))
    response = await client.generate_response(mocker.Mock(history=[], model='test-model', settings={}))
    assert response == 'Test response'

@pytest.mark.asyncio
async def test_ollama_client(mock_config, mocker):
    mocker.patch('aiohttp.ClientSession')
    client = OllamaClient(mock_config)
    
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'message': {'content': 'Test response'}}
    mocker.patch('aiohttp.ClientSession.post', return_value=mocker.AsyncMock(__aenter__=mocker.AsyncMock(return_value=mock_response)))
    
    response = await client.generate_response(mocker.Mock(history=[], model='test-model', settings={}))
    assert response == 'Test response'

@pytest.mark.asyncio
async def test_cerebras_client(mock_config, mocker):
    mocker.patch('cerebras.cloud.sdk.Cerebras')
    client = CerebrasClient(mock_config)
    assert client.client is not None

    mocker.patch.object(client.client, 'generate', return_value={'text': 'Test response'})
    response = await client.generate_response(mocker.Mock(history=[], model='test-model', settings={}))
    assert response == 'Test response'