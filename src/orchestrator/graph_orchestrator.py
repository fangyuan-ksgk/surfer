# NOTE: This file is currently not in use / deprecated.
# It has been kept for reference purposes but should not be used in active development.
# Please refer to the latest `orchestrator.py` implementation for current functionality.


from collections.abc import Callable
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx

from src.llms.anthropic import AnthropicLLM
from src.llms.openai import OpenAILLM
from src.orchestrator.utils import convert_tools_to_openai_format
from src.schemas.config import OrchestratorConfig
from src.schemas.llm import LLMConfig, LLMType
from src.utils.logging import logger


class StateGraph:
    def __init__(self):
        self.nodes: dict[str, Callable] = {}
        self.edges: dict[str, dict[str, Callable]] = {}
        self.entry_point: str = None

    def add_node(self, name: str, function: Callable):
        self.nodes[name] = function

    def add_edge(self, from_node: str, to_node: str, condition: Callable = None):
        if from_node not in self.edges:
            self.edges[from_node] = {}
        self.edges[from_node][to_node] = condition

    def set_entry_point(self, node: str):
        if node not in self.nodes:
            raise ValueError(f"Entry point {node} not found in graph")
        self.entry_point = node

    def to_networkx(self):
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node)
        for from_node, edges in self.edges.items():
            for to_node in edges:
                G.add_edge(from_node, to_node)
        return G

    def visualize(self, filename: str = "graph.png"):
        G = self.to_networkx()
        pos = nx.spring_layout(G)
        plt.figure(figsize=(12, 8))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightblue",
            node_size=3000,
            font_size=10,
            font_weight="bold",
        )
        nx.draw_networkx_labels(G, pos)
        edge_labels = {(u, v): "" for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title("State Graph Visualization")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        logger.info(f"Graph visualization saved as {filename}")


class Orchestrator:
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.agent_state = config.agent_state
        self.llm = self._get_llm(config.llm)
        self.llm_tools = convert_tools_to_openai_format(config.tools)
        self.graph = StateGraph()
        self._build_graph()

    def _get_llm(self, llm_model_name: str):
        try:
            llm_type, model_name = llm_model_name.split("/")
        except ValueError:
            raise ValueError(
                f"Invalid LLM model name format: {llm_model_name}. Expected format: 'type/model'"
            )

        if llm_type == LLMType.OPENAI.value:
            return OpenAILLM(LLMConfig(llm_type=LLMType.OPENAI, model_name=model_name))
        elif llm_type == LLMType.ANTHROPIC.value:
            return AnthropicLLM(
                LLMConfig(llm_type=LLMType.ANTHROPIC, model_name=model_name)
            )
        else:
            raise ValueError(f"Invalid LLM type: {llm_type}")

    def _build_graph(self):
        # Add nodes
        self.graph.add_node("agent", self._run_agent)
        self.graph.add_node("update_scratchpad", self._update_scratchpad)

        for tool in self.config.tools:
            tool_name = tool.__name__
            self.graph.add_node(tool_name, tool)
            self.graph.add_edge(tool_name, "update_scratchpad")

        # Add edges
        self.graph.add_edge("agent", "select_tool", self._select_tool)
        self.graph.add_edge("update_scratchpad", "agent")

        # Set entry point
        self.graph.set_entry_point("agent")

    def _run_agent(self, state: dict[str, Any]) -> dict[str, Any]:
        # Implement agent logic here
        pass

    def _update_scratchpad(self, state: dict[str, Any]) -> dict[str, Any]:
        # Implement scratchpad update logic here
        pass

    def _select_tool(self, state: dict[str, Any]) -> str:
        # Implement tool selection logic here
        pass

    def run(self):
        state = self.agent_state
        current_node = self.graph.entry_point

        while True:
            node_func = self.graph.nodes[current_node]
            state = node_func(state)

            if current_node not in self.graph.edges:
                break

            next_node = None
            for to_node, condition in self.graph.edges[current_node].items():
                if condition is None or condition(state):
                    next_node = to_node
                    break

            if next_node is None:
                break

            current_node = next_node

        return state

    def visualize_graph(self, filename: str = "orchestrator_graph.png"):
        self.graph.visualize(filename)
