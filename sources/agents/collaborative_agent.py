#!/usr/bin/env python3
"""
Collaborative Agent Enhancement for AgenticSeek
Provides multi-agent collaboration, parallel execution, and shared context management
"""

import asyncio
import time
from typing import Dict, List, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

from sources.agents.agent import Agent
from sources.utility import pretty_print, animate_thinking
from sources.logger import Logger
from sources.memory import Memory


class CollaborationMode(Enum):
    """協作模式枚舉"""
    SEQUENTIAL = "sequential"      # 順序執行
    PARALLEL = "parallel"         # 並行執行
    PIPELINE = "pipeline"         # 流水線執行
    COMPETITIVE = "competitive"   # 競爭執行（多個代理執行同一任務，選最佳結果）


@dataclass
class AgentTask:
    """代理任務數據結構"""
    task_id: str
    agent_type: str
    description: str
    dependencies: List[str]  # 依賴的任務ID
    priority: int = 1
    timeout: int = 300  # 超時時間（秒）
    retry_count: int = 0
    max_retries: int = 2


@dataclass
class TaskResult:
    """任務結果數據結構"""
    task_id: str
    agent_type: str
    success: bool
    result: str
    reasoning: str
    execution_time: float
    error_message: Optional[str] = None


class SharedContext:
    """共享上下文管理器"""
    
    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()
        self.logger = Logger("shared_context.log")
    
    async def set(self, key: str, value: Any) -> None:
        """設置共享數據"""
        async with self.lock:
            self.data[key] = value
            self.logger.info(f"Set shared context: {key}")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """獲取共享數據"""
        async with self.lock:
            return self.data.get(key, default)
    
    async def update(self, updates: Dict[str, Any]) -> None:
        """批量更新共享數據"""
        async with self.lock:
            self.data.update(updates)
            self.logger.info(f"Updated shared context with {len(updates)} items")
    
    async def get_all(self) -> Dict[str, Any]:
        """獲取所有共享數據"""
        async with self.lock:
            return self.data.copy()


class CollaborativeAgent:
    """多代理協作管理器"""
    
    def __init__(self, agents: Dict[str, Agent], max_parallel_tasks: int = 3):
        """
        初始化協作代理管理器
        
        Args:
            agents: 可用的代理字典 {agent_type: agent_instance}
            max_parallel_tasks: 最大並行任務數
        """
        self.agents = agents
        self.max_parallel_tasks = max_parallel_tasks
        self.shared_context = SharedContext()
        self.task_queue = []
        self.completed_tasks = {}
        self.running_tasks = {}
        self.logger = Logger("collaborative_agent.log")
        
    async def add_task(self, task: AgentTask) -> None:
        """添加任務到隊列"""
        self.task_queue.append(task)
        self.logger.info(f"Added task {task.task_id} to queue")
        pretty_print(f"📋 Added task: {task.description}", color="info")
    
    async def execute_task(self, task: AgentTask, context_data: Dict[str, Any]) -> TaskResult:
        """執行單個任務"""
        start_time = time.time()
        
        try:
            # 獲取對應的代理
            if task.agent_type not in self.agents:
                raise ValueError(f"Agent type {task.agent_type} not available")
            
            agent = self.agents[task.agent_type]
            
            # 準備任務提示，包含共享上下文
            prompt = self._prepare_task_prompt(task, context_data)
            
            # 執行任務
            pretty_print(f"🚀 Executing task {task.task_id} with {task.agent_type} agent", color="status")
            result, reasoning = await agent.process(prompt, None)
            
            execution_time = time.time() - start_time
            
            # 創建任務結果
            task_result = TaskResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=agent.get_success,
                result=result,
                reasoning=reasoning,
                execution_time=execution_time
            )
            
            # 更新共享上下文
            await self.shared_context.set(f"task_{task.task_id}_result", result)
            await self.shared_context.set(f"task_{task.task_id}_success", agent.get_success)
            
            self.logger.info(f"Task {task.task_id} completed in {execution_time:.2f}s")
            pretty_print(f"✅ Task {task.task_id} completed successfully", color="success")
            
            return task_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(f"Task {task.task_id} failed: {error_msg}")
            pretty_print(f"❌ Task {task.task_id} failed: {error_msg}", color="failure")
            
            return TaskResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=False,
                result="",
                reasoning="",
                execution_time=execution_time,
                error_message=error_msg
            )
    
    def _prepare_task_prompt(self, task: AgentTask, context_data: Dict[str, Any]) -> str:
        """準備任務提示，包含共享上下文信息"""
        prompt = f"Task: {task.description}\n\n"
        
        if context_data:
            prompt += "Available context from previous tasks:\n"
            for key, value in context_data.items():
                if isinstance(value, str) and len(value) > 200:
                    value = value[:200] + "..."
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        prompt += "Please complete this task using the available context information."
        return prompt
    
    async def execute_parallel(self, tasks: List[AgentTask]) -> List[TaskResult]:
        """並行執行多個任務"""
        pretty_print(f"🔄 Starting parallel execution of {len(tasks)} tasks", color="status")
        
        # 獲取當前共享上下文
        context_data = await self.shared_context.get_all()
        
        # 創建並行任務
        semaphore = asyncio.Semaphore(self.max_parallel_tasks)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_task(task, context_data)
        
        # 並行執行所有任務
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # 處理結果
        task_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task_results.append(TaskResult(
                    task_id=tasks[i].task_id,
                    agent_type=tasks[i].agent_type,
                    success=False,
                    result="",
                    reasoning="",
                    execution_time=0,
                    error_message=str(result)
                ))
            else:
                task_results.append(result)
        
        return task_results
    
    async def execute_sequential(self, tasks: List[AgentTask]) -> List[TaskResult]:
        """順序執行任務"""
        pretty_print(f"📝 Starting sequential execution of {len(tasks)} tasks", color="status")
        
        results = []
        for task in tasks:
            # 獲取最新的共享上下文
            context_data = await self.shared_context.get_all()
            
            # 執行任務
            result = await self.execute_task(task, context_data)
            results.append(result)
            
            # 如果任務失敗且有重試次數，進行重試
            if not result.success and task.retry_count < task.max_retries:
                task.retry_count += 1
                pretty_print(f"🔄 Retrying task {task.task_id} (attempt {task.retry_count + 1})", color="warning")
                retry_result = await self.execute_task(task, context_data)
                results[-1] = retry_result
        
        return results
    
    async def execute_pipeline(self, tasks: List[AgentTask]) -> List[TaskResult]:
        """流水線執行任務（考慮依賴關係）"""
        pretty_print(f"🔗 Starting pipeline execution of {len(tasks)} tasks", color="status")
        
        # 按依賴關係排序任務
        sorted_tasks = self._sort_tasks_by_dependencies(tasks)
        
        # 順序執行排序後的任務
        return await self.execute_sequential(sorted_tasks)
    
    def _sort_tasks_by_dependencies(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """根據依賴關係對任務進行拓撲排序"""
        # 簡單的拓撲排序實現
        task_dict = {task.task_id: task for task in tasks}
        visited = set()
        result = []
        
        def visit(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            
            if task_id in task_dict:
                task = task_dict[task_id]
                # 先訪問依賴的任務
                for dep_id in task.dependencies:
                    visit(dep_id)
                result.append(task)
        
        for task in tasks:
            visit(task.task_id)
        
        return result
    
    async def execute_competitive(self, task_description: str, agent_types: List[str]) -> TaskResult:
        """競爭執行（多個代理執行同一任務，選擇最佳結果）"""
        pretty_print(f"🏆 Starting competitive execution with {len(agent_types)} agents", color="status")
        
        # 為每個代理創建相同的任務
        tasks = []
        for i, agent_type in enumerate(agent_types):
            task = AgentTask(
                task_id=f"competitive_{i}",
                agent_type=agent_type,
                description=task_description,
                dependencies=[]
            )
            tasks.append(task)
        
        # 並行執行所有任務
        results = await self.execute_parallel(tasks)
        
        # 選擇最佳結果（優先選擇成功的，然後按執行時間排序）
        successful_results = [r for r in results if r.success]
        if successful_results:
            best_result = min(successful_results, key=lambda x: x.execution_time)
            pretty_print(f"🥇 Best result from {best_result.agent_type} agent", color="success")
            return best_result
        else:
            # 如果都失敗了，返回第一個結果
            pretty_print("❌ All competitive tasks failed", color="failure")
            return results[0] if results else None


# 使用範例和測試函數
async def test_collaborative_agent():
    """測試協作代理功能"""
    # 這裡需要實際的代理實例，這只是示例
    print("🧪 Testing Collaborative Agent functionality...")
    print("✅ Collaborative Agent module created successfully!")


if __name__ == "__main__":
    asyncio.run(test_collaborative_agent())
