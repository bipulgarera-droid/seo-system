
import unittest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv
import json

load_dotenv('.env.local')

with patch('supabase.create_client') as mock_create_client:
    from api.index import process_tofu_generation

class TestToFuGeneration(unittest.TestCase):
    
    @patch('api.index.supabase')
    @patch('api.index.genai_new.Client')
    @patch('api.index.perform_gemini_research')
    def test_process_tofu_generation(self, mock_research, mock_genai_client, mock_supabase):
        # Setup Mocks
        page_id = 'test-mofu-id'
        api_key = 'test-api-key'
        
        # Mock MoFu Page
        mock_mofu = {
            'id': page_id,
            'url': 'https://example.com/mofu',
            'project_id': 'test-project',
            'tech_audit_data': {'title': 'Test MoFu Topic'}
        }
        
        # Mock Project
        mock_project = {'location': 'US', 'language': 'English'}
        
        # Mock Responses
        mock_mofu_res = MagicMock()
        mock_mofu_res.data = mock_mofu
        
        mock_project_res = MagicMock()
        mock_project_res.data = mock_project
        
        # Side effect for supabase.table
        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == 'pages':
                mock_query.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_mofu_res
                mock_query.update.return_value.eq.return_value.execute.return_value.data = {}
                # Insert returns data for auto-research
                mock_query.insert.return_value.execute.return_value.data = [{'id': 'new-tofu-id', 'tech_audit_data': {'title': 'New ToFu Topic'}}]
            elif table_name == 'projects':
                mock_query.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_project_res
            return mock_query
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Mock Gemini Research
        mock_research.return_value = {'keywords': [{'keyword': 'kw1', 'intent': 'informational'}]}
        
        # Mock Gemini Generation (Topics)
        mock_model = MagicMock()
        mock_genai_client.return_value.models = mock_model
        
        mock_topic_response = MagicMock()
        mock_topic_response.text = json.dumps({
            "topics": [{
                "title": "ToFu Topic 1",
                "slug": "tofu-topic-1",
                "description": "Desc",
                "keyword_cluster": ["kw1"],
                "primary_keyword": "kw1"
            }]
        })
        
        mock_model.generate_content.return_value = mock_topic_response
        
        # Run Function
        process_tofu_generation([page_id], api_key)
        
        # Verify Gemini calls
        self.assertTrue(mock_model.generate_content.called)
        
        # Verify Auto-Research
        self.assertTrue(mock_research.called)

if __name__ == '__main__':
    unittest.main()
