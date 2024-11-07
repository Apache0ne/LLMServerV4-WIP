import pytest
from game.engine import GameEngine
from game.state import GameState

@pytest.fixture
def mock_services(mocker):
    return {
        'test_context': mocker.Mock(service='groq')
    }

@pytest.fixture
def game_engine(mock_services):
    return GameEngine(mock_services)

@pytest.mark.asyncio
async def test_start_game(game_engine, mocker):
    mocker.patch.object(game_engine, '_generate_response', return_value={
        'narration': 'Test narration',
        'image': {'top': 'Top', 'bottom': 'Bottom', 'prompt': 'Image prompt'},
        'actions': [{'description': 'Action 1'}, {'description': 'Action 2'}]
    })
    
    result = await game_engine.start_game('test_context')
    assert 'narration' in result
    assert 'image' in result
    assert 'actions' in result
    assert 'test_context' in game_engine.states

@pytest.mark.asyncio
async def test_process_turn(game_engine, mocker):
    game_engine.states['test_context'] = GameState('test_context', {})
    
    mocker.patch.object(game_engine, '_generate_response', return_value={
        'narration': 'Turn narration',
        'image': {'top': 'Top', 'bottom': 'Bottom', 'prompt': 'Image prompt'},
        'actions': [{'description': 'Action 1'}, {'description': 'Action 2'}]
    })
    
    result = await game_engine.process_turn('test_context', 'Test action')
    assert 'narration' in result
    assert 'image' in result
    assert 'actions' in result

def test_end_game(game_engine):
    game_engine.states['test_context'] = GameState('test_context', {})
    game_engine.end_game('test_context')
    assert 'test_context' not in game_engine.states