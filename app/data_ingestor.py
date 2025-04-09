"""Module for ingesting CSV data and computing statistics."""
import csv
from collections import defaultdict

class DataIngestor:
    """Class for reading CSV data and computing various statistics."""
    def __init__(self, csv_path: str):
        self.data = []

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.data.append({
                    'state': row['LocationDesc'],
                    'question': row['Question'],
                    'data_value': row['Data_Value'],
                    'strat_category' : row['StratificationCategory1'],
                    'strat' : row['Stratification1']
                })

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            "Percent of adults who achieve at least 150 minutes a week of moderate-intensity "
            "aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity"
            " (or an equivalent combination)",
            "Percent of adults who achieve at least 150 minutes a week of moderate-intensity "
            "aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical"
            " activity and engage in muscle-strengthening activities on 2 or more days a week",
            "Percent of adults who achieve at least 300 minutes a week of moderate-intensity"
            " aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity"
            " (or an equivalent combination)",
            "Percent of adults who engage in muscle-strengthening activities on 2 or more"
            " days a week",
        ]

    def get_values(self, question, state=None):
        """Helper to extract float values for a given question (and optionally,
        a specific state)."""
        values = []

        #Extract the needed data 
        for row in self.data:
            if row['question'] != question:
                continue

            if state and row['state'] != state:
                continue

            try:
                values.append(float(row['data_value']))
            except (ValueError, TypeError):
                continue

        return values

    def get_statewise_values(self, question):
        """Helper to return a dictionary: state -> list of values for the given question."""
        states = {}

        #Group values by state
        for row in self.data:
            if row['question'] != question:
                continue

            state = row['state']
            try:
                value = float(row['data_value'])
            except (ValueError, TypeError):
                continue

            if state not in states:
                states[state] = []

            states[state].append(value)

        return states


    def compute_global_mean(self, data):
        """Compute the global mean for the specified question."""
        question = data['question']
        values = self.get_values(question)

        return sum(values) / len(values) if values else None


    def compute_state_mean(self, data):
        """Compute the mean for the specified question for a particular state."""
        question = data['question']
        state = data['state']
        values = self.get_values(question, state)

        return {state: sum(values) / len(values)} if values else {}


    def compute_states_mean(self, data):
        """Compute the mean for the specified question for all states."""
        question = data['question']
        statewise = self.get_statewise_values(question)
        mean_states = {state: sum(vals)/len(vals) for state, vals in statewise.items()}

        return dict(sorted(mean_states.items(), key=lambda x: x[1]))


    def compute_best5(self, data):
        """Return top 5 best states based on the question type (min or max)."""
        question = data['question']

        if question not in self.questions_best_is_min and question not in self.questions_best_is_max:
            return {}
        state_info = self.get_statewise_values(question)

        mean_states = {state: sum(values) / len(values) for state, values in state_info.items()}

        if not mean_states:
            return {}

        if question in self.questions_best_is_min:
            sorted_states = sorted(mean_states.items(), key=lambda x: x[1])
        else:
            sorted_states = sorted(mean_states.items(), key=lambda x: x[1], reverse=True)

        return dict(sorted_states[:5])


    def compute_worst5(self, data):
        """Return top 5 best states based on the question type (min or max better)."""
        question = data['question']
    
        if question not in self.questions_best_is_min and question not in self.questions_best_is_max:
            return {}

        state_info = self.get_statewise_values(question)
        mean_states = {state: sum(values) / len(values) for state, values in state_info.items()}

        if not mean_states:
            return {}

        if question in self.questions_best_is_min:
            sorted_states = sorted(mean_states.items(), key=lambda x: x[1], reverse=True)
        else:
            sorted_states = sorted(mean_states.items(), key=lambda x: x[1])

        return dict(sorted_states[:5])


    def compute_diff_from_mean(self, data):
        """Return a dictionary with state names as keys and the difference from the global 
        mean as values."""
        question = data['question']

        values_by_state = self.get_statewise_values(question)
        global_mean = self.compute_global_mean(data)

        if not values_by_state or global_mean is None:
            return {}

        result = {}
        for state, values in values_by_state.items():
            if not values:
                continue
            state_mean = sum(values) / len(values)
            result[state] = round(global_mean - state_mean, 6)

        return result


    def compute_diff_from_state_mean(self, data):
        """Return a dictionary with state names as keys and the difference from the state 
        mean as values."""
        question = data['question']
        state = data['state']

        global_mean = self.compute_global_mean(data)
        values = self.get_values(question, state)

        if not values or global_mean is None:
            return {}

        state_mean = sum(values) / len(values)

        return {state: round(global_mean - state_mean, 6)}
    
    def compute_mean_by_category(self, data):
        """
        Return a list of dicts with columns: State, Category, Subgroup, Value.
        This computes the mean Data_Value for each (State, StratificationCategory1, Stratification1).
        """
        question = data['question']
        results = {}

        #Iterate over the data and compute the mean for each category
        for row in self.data:
            if row['question'] != question:
                continue

            state = row['state']
            category = row['strat_category']
            subgroup = row['strat']

            if not category or not subgroup:
                continue

            try:
                value = float(row['data_value'])
            except (ValueError, TypeError):
                continue

            key = str((state, category, subgroup))
            
            if key not in results:
                results[key] = []

            results[key].append(value)

        mean_results = {key: sum(values) / len(values) for key, values in results.items()}

        return mean_results


    def compute_state_mean_by_category(self, data):
        """Same as before but now there is also a state given as parameter
        so the operations are done only for that specific state
        """
        question = data['question']
        state = data['state']
        results = {}

        for row in self.data:
            if row['question'] != question or row['state'] != state:
                continue

            category = row['strat_category']
            subgroup = row['strat']

            if not category or not subgroup:
                continue

            try:
                value = float(row['data_value'])
            except (ValueError, TypeError):
                continue

            key = str((category, subgroup))

            if key not in results:
                results[key] = []

            results[key].append(value)

        mean_results = {key: round(sum(vals) / len(vals), 6) for key, vals in results.items()}

        return {state: mean_results}
