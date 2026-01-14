# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Guarded workflow wrapper using NeMo Guardrails."""

import os
from pathlib import Path
from typing import Optional

from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions.actions import ActionResult


class GuardedWorkflow:
    """Wrapper class that adds NeMo Guardrails to a NAT workflow."""
    
    def __init__(self, workflow, guardrails_config_path: Optional[str] = None):
        """Initialize guarded workflow.
        
        Args:
            workflow: The NAT workflow to wrap
            guardrails_config_path: Path to guardrails config directory.
                                   If None, uses default guardrails_config directory.
        """
        self.workflow = workflow
        
        # Set guardrails config path
        if guardrails_config_path is None:
            # Default to guardrails_config directory in the example
            current_dir = Path(__file__).parent.parent.parent
            guardrails_config_path = str(current_dir / "guardrails_config")
        
        # Load guardrails configuration
        self.config = RailsConfig.from_path(guardrails_config_path)
        self.rails = LLMRails(self.config)
        
        # Register custom actions
        self._register_actions()
    
    def _register_actions(self):
        """Register custom guardrails actions."""
        from guardrails_config.actions import (
            check_jailbreak,
            check_blocked_terms,
            check_input_length,
            check_output_relevance,
            check_politics,
        )
        
        self.rails.register_action(check_jailbreak, "check_jailbreak")
        self.rails.register_action(check_blocked_terms, "check_blocked_terms")
        self.rails.register_action(check_input_length, "check_input_length")
        self.rails.register_action(check_output_relevance, "check_output_relevance")
        self.rails.register_action(check_politics, "check_politics")
    
    async def ainvoke(self, user_input: str) -> str:
        """Process user input through guardrails and workflow.
        
        Args:
            user_input: The user's input message
            
        Returns:
            The guarded response from the workflow
        """
        # Apply input guardrails
        input_rails_result = await self.rails.generate_async(
            messages=[{"role": "user", "content": user_input}]
        )
        
        # Check if input was blocked
        if isinstance(input_rails_result, ActionResult):
            if input_rails_result.is_stop:
                return input_rails_result.return_value or "I'm unable to process that request."
        
        # Extract the processed input
        if isinstance(input_rails_result, dict):
            processed_input = input_rails_result.get("content", user_input)
        elif hasattr(input_rails_result, "content"):
            processed_input = input_rails_result.content
        else:
            processed_input = str(input_rails_result)
        
        # Run the original NAT workflow
        try:
            workflow_result = await self.workflow.ainvoke(processed_input)
        except Exception as e:
            return f"An error occurred while processing your request: {str(e)}"
        
        # Apply output guardrails
        output_rails_result = await self.rails.generate_async(
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": str(workflow_result)}
            ]
        )
        
        # Check if output was blocked
        if isinstance(output_rails_result, ActionResult):
            if output_rails_result.is_stop:
                return output_rails_result.return_value or "I can only provide information about Dynatrace."
        
        # Extract the final response
        if isinstance(output_rails_result, dict):
            final_response = output_rails_result.get("content", workflow_result)
        elif hasattr(output_rails_result, "content"):
            final_response = output_rails_result.content
        else:
            final_response = str(workflow_result)
        
        return final_response
    
    async def astream(self, user_input: str):
        """Stream workflow results through guardrails.
        
        Args:
            user_input: The user's input message
            
        Yields:
            Chunks of the guarded response
        """
        # For simplicity, we'll collect the full response and yield it
        # More sophisticated implementations could stream guardrails checks
        result = await self.ainvoke(user_input)
        yield result


def create_guarded_workflow(workflow, guardrails_config_path: Optional[str] = None):
    """Factory function to create a guarded workflow.
    
    Args:
        workflow: The NAT workflow to wrap
        guardrails_config_path: Path to guardrails config directory
        
    Returns:
        GuardedWorkflow instance
    """
    return GuardedWorkflow(workflow, guardrails_config_path)
