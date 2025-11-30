
import unittest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv

# Load env vars to avoid import errors
load_dotenv('.env.local')

# Mock Supabase before importing api.index
with patch('supabase.create_client') as mock_create_client:
    from api.index import process_content_generation

class TestContentGeneration(unittest.TestCase):
    
    @patch('api.index.supabase')
    @patch('api.index.genai_new.Client')
    @patch('api.index.scrape_page_content')
    def test_process_content_generation_product(self, mock_scrape, mock_genai_client, mock_supabase):
        # Setup Mocks
        page_id = 'test-page-id'
        api_key = 'test-api-key'
        
        # Mock Page Data
        mock_page = {
            'id': page_id,
            'url': 'https://example.com/product',
            'project_id': 'test-project',
            'page_type': 'Product',
            'tech_audit_data': {'title': 'Test Product', 'body_content': ''} # Empty content to trigger scrape
        }
        
        # Mock Responses
        mock_page_res = MagicMock()
        mock_page_res.data = mock_page
        
        mock_project_res = MagicMock()
        mock_project_res.data = {'location': 'US', 'language': 'English'}
        
        # Configure side_effect for table()
        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == 'pages':
                mock_query.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_page_res
                # Also handle update() for pages
                mock_query.update.return_value.eq.return_value.execute.return_value.data = {}
            elif table_name == 'projects':
                mock_query.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_project_res
            return mock_query
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Mock Scrape
        mock_scrape.return_value = {'body_content': 'Scraped Content', 'title': 'Scraped Title'}
        
        # Mock Gemini
        mock_model = MagicMock()
        mock_genai_client.return_value.models = mock_model
        mock_model.generate_content.return_value.text = "Generated Content\n**Meta Description**: New Meta"
        
        # Run Function
        process_content_generation([page_id], api_key)
        
        # Verify Scrape was called (because body_content was empty)
        mock_scrape.assert_called_with('https://example.com/product')
        
        # Verify Gemini was called
        mock_model.generate_content.assert_called()
        args, kwargs = mock_model.generate_content.call_args
        self.assertIn("Generated Content", str(mock_model.generate_content.return_value.text))
        
        # Verify DB Update
        # Should update twice: once for scrape, once for generation
        # We can check if table('pages') was called
        self.assertTrue(mock_supabase.table.called)

    @patch('api.index.supabase')
    @patch('api.index.genai_new.Client')
    def test_process_content_generation_topic(self, mock_genai_client, mock_supabase):
        # Setup Mocks
        page_id = 'test-topic-id'
        api_key = 'test-api-key'
        
        # Mock Page Data
        mock_page = {
            'id': page_id,
            'url': 'https://example.com/topic',
            'project_id': 'test-project',
            'page_type': 'Topic',
            'funnel_stage': 'MoFu',
            'tech_audit_data': {'title': 'Test Topic'},
            'research_data': {'formatted_keywords': 'kw1', 'perplexity_research': 'research'}
        }
        
        # Mock Responses
        mock_page_res = MagicMock()
        mock_page_res.data = mock_page
        
        mock_project_res = MagicMock()
        mock_project_res.data = {'location': 'US', 'language': 'English'}
        
        # Configure side_effect for table()
        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == 'pages':
                mock_query.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_page_res
                mock_query.update.return_value.eq.return_value.execute.return_value.data = {}
            elif table_name == 'projects':
                mock_query.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_project_res
            return mock_query
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Mock Gemini
        mock_model = MagicMock()
        mock_genai_client.return_value.models = mock_model
        mock_model.generate_content.return_value.text = "Generated Topic Content"
        
        # Run Function
        process_content_generation([page_id], api_key)
        
        # Verify Gemini was called with Topic prompt
        mock_model.generate_content.assert_called()
        args, kwargs = mock_model.generate_content.call_args
        prompt = args[1] if len(args) > 1 else kwargs.get('contents')
        self.assertIn("**ARTICLE TYPE**: MoFu Content", prompt)

if __name__ == '__main__':
    unittest.main()
