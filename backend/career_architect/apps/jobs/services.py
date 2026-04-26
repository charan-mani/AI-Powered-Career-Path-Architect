import requests
import os
import logging

logger = logging.getLogger(__name__)

class AdzunaJobClient:
    """Client for Adzuna Job API"""
    
    def __init__(self):
        self.app_id = os.environ.get('ADZUNA_APP_ID')
        self.app_key = os.environ.get('ADZUNA_APP_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        
    def search_jobs(self, params):
        """
        Search for jobs using Adzuna API
        """
        if not self.app_id or not self.app_key:
            logger.error("Adzuna API credentials not configured")
            return {'results': [], 'count': 0}
        
        country = params.get('country', 'us')
        what = params.get('what', '')
        where = params.get('where', '')
        page = params.get('page', 1)
        
        # Build URL
        url = f"{self.base_url}/{country}/search/{page}"
        
        # Build query parameters
        query_params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': 20,
            'content-type': 'application/json',
        }
        
        if what:
            query_params['what'] = what
        if where:
            query_params['where'] = where
            
        # Add filters
        if params.get('salary_min'):
            query_params['salary_min'] = params['salary_min']
            
        if params.get('full_time') == 'true':
            query_params['full_time'] = 1
            
        if params.get('permanent') == 'true':
            query_params['permanent'] = 1
            
        if params.get('contract') == 'true':
            query_params['contract'] = 1
            
        if params.get('days_old'):
            query_params['max_days_old'] = params['days_old']
        
        logger.info(f"Calling Adzuna API: {url}")
        
        try:
            response = requests.get(url, params=query_params, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Found {data.get('count', 0)} jobs")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API error: {e}")
            return {'results': [], 'count': 0, 'error': str(e)}
    
    def get_job_details(self, job_id, country='us'):
        """Get details for a specific job"""
        url = f"{self.base_url}/{country}/jobs/{job_id}"
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None