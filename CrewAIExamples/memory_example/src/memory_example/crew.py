from typing import Any, Dict, Optional
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool,before_kickoff,after_kickoff,cache_handler,callback
from datetime import datetime
import os

import json

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class MemoryExample():
	"""MemoryExample crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	@agent
	def email_summarizer(self) -> Agent:
		return Agent(
			config=self.agents_config['email_summarizer'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@task
	def email_summarizer_task(self) -> Task:
		return Task(
			config=self.tasks_config['email_summarizer_task'],
			output_file='report.md'
		)


	@crew
	def crew(self) -> Crew:
		"""Creates the MemoryExample crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
	

	@tool
	def web_search_tool(query: str, max_results: int = 5) -> list[str]:
		"""
		Search the web for information.

		Args:
			query: The search query
			max_results: Maximum number of results to return

		Returns:
			List of search results
		"""
		# Implement your search logic here
		return [f"Result {i} for: {query}" for i in range(max_results)]

	@before_kickoff
	def validate_inputs(self, inputs: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
		"""Validate and preprocess inputs before the crew starts."""
		if inputs is None:
			return None
			
		if 'topic' not in inputs:
			raise ValueError("Topic is required")
		
		# Add additional context
		inputs['timestamp'] = datetime.now().isoformat()
		inputs['topic'] = inputs['topic'].strip().lower()
		return inputs
	

	# @after_kickoff
	# def process_results(self, result: CrewOutput) -> CrewOutput:
	# 	"""Process and format the results after the crew completes."""
	# 	result.raw = result.raw.strip()
	# 	result.raw = f"""
	# 	# Research Results
	# 	Generated on: {datetime.now().isoformat()}
		
	# 	{result.raw}
	# 	"""
	# 	return result
	

	@callback
	def log_task_completion(self, task: Task, output: str):
		"""Log task completion details for monitoring."""
		print(f"Task '{task.description}' completed")
		print(f"Output length: {len(output)} characters")
		print(f"Agent used: {task.agent.role}")
		print("-" * 50)

	@cache_handler
	def custom_cache(self, key: str) -> Optional[str]:
		"""Custom cache implementation for storing task results."""
		cache_file = f"cache/{key}.json"
		
		if os.path.exists(cache_file):
			with open(cache_file, 'r') as f:
				data = json.load(f)
				# Check if cache is still valid (e.g., not expired)
				if datetime.fromisoformat(data['timestamp']) > datetime.now() - datetime.timedelta(days=1):
					return data['result']
		return None