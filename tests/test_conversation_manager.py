import pytest
from conversation_manager import ConversationManager, ConversationContext

@pytest.fixture
def conversation_manager():
    return ConversationManager()

def test_create_context(conversation_manager):
    result = conversation_manager.create_context('test', 'groq', 'test-model', 'System prompt')
    assert result['success'] == True
    assert 'test' in conversation_manager.contexts

def test_list_contexts(conversation_manager):
    conversation_manager.create_context('test1', 'groq', 'test-model', 'System prompt')
    conversation_manager.create_context('test2', 'ollama', 'test-model', 'System prompt')
    result = conversation_manager.list_contexts()
    assert len(result['contexts']) == 2
    assert result['contexts'][0]['name'] == 'test1'
    assert result['contexts'][1]['name'] == 'test2'

def test_delete_context(conversation_manager):
    conversation_manager.create_context('test', 'groq', 'test-model', 'System prompt')
    result = conversation_manager.delete_context('test')
    assert result['success'] == True
    assert 'test' not in conversation_manager.contexts

def test_get_context(conversation_manager):
    conversation_manager.create_context('test', 'groq', 'test-model', 'System prompt')
    context = conversation_manager.get_context('test')
    assert isinstance(context, ConversationContext)
    assert context.name == 'test'