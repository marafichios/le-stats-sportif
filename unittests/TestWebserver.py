import unittest
import json
from deepdiff import DeepDiff
from app.data_ingestor import DataIngestor

class TestWebserver(unittest.TestCase):
    
    def setUp(self):
        """Set up necessary data and data_ingestor instance for testing."""
        self.data_ingestor = DataIngestor('./unittests/unittesting.csv')
    

    def test_global_mean(self):
        """Test the global mean calculation."""
        job = self.data_ingestor.compute_global_mean({'question': 'Percent of adults aged 18 years and older who have obesity'})
        ref_file = './unittests/results/global_mean.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_mean_by_category(self):
        """Test the state mean calculation."""
        job = self.data_ingestor.compute_mean_by_category({'question': 'Percent of adults aged 18 years and older who have obesity', 'state': 'North Carolina'})
        
        ref_file = './unittests/results/mean_by_category.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_best5(self):
        """Test the best 5 states for a given question."""
        job = self.data_ingestor.compute_best5({'question': 'Percent of adults who engage in no leisure-time physical activity'})
        
        ref_file = './unittests/results/best5.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_worst5(self):
        """Test the worst 5 states for a given question."""
        job = self.data_ingestor.compute_worst5({'question': 'Percent of adults who engage in no leisure-time physical activity'})
        
        ref_file = './unittests/results/worst5.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_state_mean(self):
        """Test the state mean calculation for a specific state."""
        job = self.data_ingestor.compute_state_mean({'question': 'Percent of adults who report consuming fruit less than one time daily', 'state': 'North Dakota'})
        
        ref_file = './unittests/results/state_mean.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_state_diff_from_mean(self):
        """Test the state difference from mean calculation."""
        job = self.data_ingestor.compute_diff_from_state_mean({'question': 'Percent of adults who report consuming fruit less than one time daily', 'state': 'North Dakota'})
        
        ref_file = './unittests/results/state_diff_from_mean.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_states_mean(self):
        """Test the states mean calculation."""
        job = self.data_ingestor.compute_states_mean({'question': 'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week'})
        
        ref_file = './unittests/results/states_mean.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_diff_from_mean(self):
        """Test the difference from mean calculation."""
        job = self.data_ingestor.compute_diff_from_mean({'question': 'Percent of adults who engage in no leisure-time physical activity'})
        
        ref_file = './unittests/results/diff_from_mean.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    def test_state_mean_by_category(self):
        """Test the state mean calculation for a specific state."""
        job = self.data_ingestor.compute_state_mean_by_category({'question': 'Percent of adults who report consuming fruit less than one time daily', 'state': 'North Dakota'})
        
        ref_file = './unittests/results/state_mean_by_category.json'
        with open(ref_file, 'r') as file:
            ref_data = json.load(file)
        
        self.assertEqual(DeepDiff(job, ref_data, math_epsilon=0.01), {})

    
    def tearDown(self):
        """Clean up any resources used in the tests."""
        pass
