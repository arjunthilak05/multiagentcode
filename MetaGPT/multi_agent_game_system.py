#!/usr/bin/env python3
"""
Proper MetaGPT Multi-Agent Educational Game Generation System
Following the correct MetaGPT framework patterns
"""

import json
import re
import asyncio
from pathlib import Path
from typing import Dict, List

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team
from metagpt.config2 import Config


def parse_json_response(rsp: str) -> Dict:
    """Extract JSON from AI response"""
    # Try to find JSON in code blocks first
    json_pattern = r"```json\s*\n?(.*?)\n?```"
    match = re.search(json_pattern, rsp, re.DOTALL | re.IGNORECASE)
    if match:
        json_text = match.group(1)
    else:
        # Try to find JSON object directly
        json_pattern = r"\{.*?\}"
        match = re.search(json_pattern, rsp, re.DOTALL)
        json_text = match.group(0) if match else rsp
    
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        # Return basic structure if parsing fails
        return {"error": "Failed to parse JSON", "raw_response": rsp}


def parse_html_response(rsp: str) -> str:
    """Extract HTML from AI response"""
    # Remove markdown code blocks
    html_pattern = r"```html\s*\n?(.*?)\n?```"
    match = re.search(html_pattern, rsp, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Check if it's already clean HTML
    if rsp.strip().startswith('<!DOCTYPE html>') or rsp.strip().startswith('<html'):
        return rsp.strip()
    
    return rsp


# ================== ACTIONS ==================

class AnalyzeContent(Action):
    """Action: Analyze educational content to determine optimal game count"""
    
    PROMPT_TEMPLATE: str = """
    Analyze this educational content and determine the optimal number of interactive games needed to COMPLETELY teach this material.

    CONTENT TO ANALYZE:
    {content}

    Your task:
    1. Identify ALL distinct learning concepts that need separate games
    2. Determine the complexity level of each concept  
    3. Calculate how many games are needed for complete mastery
    4. Ensure no concept is left untaught

    ANALYSIS CRITERIA:
    - Simple concepts: 1 game
    - Medium concepts: 2-3 games  
    - Complex concepts: 3-4 games
    - Minimum 3 games, Maximum 15 games
    - Each game must teach something unique and essential
    - Progressive difficulty from foundational to advanced

    Return JSON with this structure:
    {{
        "content_analysis": {{
            "total_concepts": number,
            "complexity_breakdown": {{"simple": n, "medium": n, "complex": n}},
            "estimated_learning_time": "X minutes",
            "optimal_game_count": number,
            "reasoning": "Why this number of games is perfect"
        }},
        "game_specifications": [
            {{
                "game_number": 1,
                "title": "Game Title",
                "concept": "Specific learning concept", 
                "difficulty": "Very Easy|Easy|Medium|Hard|Very Hard",
                "learning_objective": "What students will master",
                "game_type": "identification|pattern|creation|application|quiz",
                "estimated_time": "X minutes",
                "prerequisites": ["Previous concepts needed"],
                "builds_toward": ["Future concepts this enables"]
            }}
        ]
    }}

    Return ONLY valid JSON, no explanations.
    """
    
    name: str = "AnalyzeContent"

    async def run(self, content: str) -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content)
        rsp = await self._aask(prompt)
        return rsp


class GenerateGamePrompt(Action):
    """Action: Generate detailed prompts for game creation"""
    
    PROMPT_TEMPLATE: str = """
    Create a detailed game generation prompt for this educational game specification:

    GAME SPEC:
    {game_spec}

    CONTEXT:
    - This is game {game_position} of {total_games} in a learning sequence
    - Target: Grade 6 students (ages 11-12)
    - Must be HTML5 with embedded CSS/JavaScript

    Create a comprehensive prompt that will generate a perfect educational game.
    The prompt should specify:
    - Educational objectives and pedagogy
    - Technical requirements (HTML5, mobile-responsive, accessible)
    - Game mechanics and interactivity
    - Visual design and UX
    - Assessment and feedback systems

    Return the complete prompt text that will be used to generate the game.
    """
    
    name: str = "GenerateGamePrompt"

    async def run(self, game_spec: str, game_position: int, total_games: int) -> str:
        prompt = self.PROMPT_TEMPLATE.format(
            game_spec=game_spec,
            game_position=game_position,
            total_games=total_games
        )
        rsp = await self._aask(prompt)
        return rsp


class CreateGame(Action):
    """Action: Generate complete HTML5 educational games"""
    
    PROMPT_TEMPLATE: str = """
    {detailed_prompt}

    IMPORTANT REQUIREMENTS:
    - Return ONLY the complete HTML code
    - Single file with embedded CSS and JavaScript
    - Mobile-responsive design
    - Accessible (WCAG guidelines)
    - Interactive with immediate feedback
    - Sound effects using Web Audio API
    - Engaging animations and transitions
    - Educational effectiveness is priority #1

    Generate the complete, working HTML5 game now.
    """
    
    name: str = "CreateGame"

    async def run(self, detailed_prompt: str) -> str:
        prompt = self.PROMPT_TEMPLATE.format(detailed_prompt=detailed_prompt)
        rsp = await self._aask(prompt)
        return rsp


class ValidateGame(Action):
    """Action: Validate and score educational games"""
    
    PROMPT_TEMPLATE: str = """
    Validate this HTML5 educational game and provide a quality score.

    GAME HTML:
    {game_html}

    ORIGINAL SPECIFICATION:
    {game_spec}

    Evaluation Criteria:
    1. Educational Effectiveness (40%) - Does it teach the concept well?
    2. Technical Quality (25%) - Is the code clean and functional?
    3. User Experience (20%) - Is it engaging and intuitive?
    4. Accessibility (15%) - Can all students use it?

    Return JSON:
    {{
        "validation_score": 0-10,
        "educational_effectiveness": 0-10,
        "technical_quality": 0-10,
        "user_experience": 0-10,
        "accessibility": 0-10,
        "issues_found": ["list of any problems"],
        "recommendations": ["suggestions for improvement"],
        "passes_validation": true/false
    }}
    """
    
    name: str = "ValidateGame"

    async def run(self, game_html: str, game_spec: str) -> str:
        prompt = self.PROMPT_TEMPLATE.format(
            game_html=game_html[:2000],  # Limit length for API
            game_spec=game_spec
        )
        rsp = await self._aask(prompt)
        return rsp


# ================== ROLES ==================

class ContentAnalyst(Role):
    """Role: Analyzes educational content and determines optimal game structure"""
    
    name: str = "ContentAnalyst"
    profile: str = "Educational Content Analyst"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([AnalyzeContent])


class GameDesigner(Role):
    """Role: Designs detailed game specifications and prompts"""
    
    name: str = "GameDesigner"
    profile: str = "Educational Game Designer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GenerateGamePrompt])
        self._watch([AnalyzeContent])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        
        # Get content analysis from memory
        analysis_memory = self.get_memories(k=1)[0].content
        analysis_data = parse_json_response(analysis_memory)
        
        # Generate prompts for each game
        game_prompts = []
        games = analysis_data.get("game_specifications", [])
        total_games = len(games)
        
        for i, game_spec in enumerate(games, 1):
            game_spec_str = json.dumps(game_spec, indent=2)
            prompt = await todo.run(game_spec_str, i, total_games)
            game_prompts.append({
                "game_number": i,
                "prompt": prompt,
                "spec": game_spec
            })
        
        prompts_json = json.dumps(game_prompts, indent=2)
        msg = Message(content=prompts_json, role=self.profile, cause_by=type(todo))
        return msg


class GameDeveloper(Role):
    """Role: Develops actual HTML5 games from specifications"""
    
    name: str = "GameDeveloper"
    profile: str = "HTML5 Game Developer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreateGame])
        self._watch([GenerateGamePrompt])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        
        # Get game prompts from memory
        prompts_memory = self.get_memories(k=1)[0].content
        game_prompts = json.loads(prompts_memory)
        
        # Generate all games
        generated_games = []
        for prompt_data in game_prompts:
            logger.info(f"Generating game {prompt_data['game_number']}: {prompt_data['spec']['title']}")
            
            game_html = await todo.run(prompt_data["prompt"])
            clean_html = parse_html_response(game_html)
            
            generated_games.append({
                "game_number": prompt_data["game_number"],
                "title": prompt_data["spec"]["title"],
                "html": clean_html,
                "spec": prompt_data["spec"]
            })
        
        games_json = json.dumps(generated_games, indent=2)
        msg = Message(content=games_json, role=self.profile, cause_by=type(todo))
        return msg


class GameValidator(Role):
    """Role: Validates and ensures quality of generated games"""
    
    name: str = "GameValidator"
    profile: str = "Educational Game Quality Assurance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ValidateGame])
        self._watch([CreateGame])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        
        # Get generated games from memory
        games_memory = self.get_memories(k=1)[0].content
        games_data = json.loads(games_memory)
        
        # Validate all games
        validation_results = []
        for game in games_data:
            logger.info(f"Validating game: {game['title']}")
            
            validation = await todo.run(game["html"], json.dumps(game["spec"]))
            validation_data = parse_json_response(validation)
            
            validation_results.append({
                "game_number": game["game_number"],
                "title": game["title"],
                "validation": validation_data,
                "game_data": game
            })
        
        results_json = json.dumps(validation_results, indent=2)
        msg = Message(content=results_json, role=self.profile, cause_by=type(todo))
        return msg


# ================== MAIN SYSTEM ==================

class MultiAgentGameSystem:
    """Complete Multi-Agent Educational Game Generation System"""
    
    def __init__(self, config_path: str = "config/config2.yaml"):
        self.config = Config.from_yaml_file(Path(config_path))
        logger.info(f"🤖 Multi-Agent Game System initialized")

    async def generate_educational_games(
        self, 
        content_file: str = "extract (1).txt",
        output_dir: str = "multi_agent_games",
        n_rounds: int = 4
    ):
        """Generate games using multi-agent collaboration"""
        
        logger.info(f"🚀 Starting multi-agent game generation")
        
        # Load content
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create team with proper startup
        team = Team()
        team.hire([
            ContentAnalyst(),
            GameDesigner(), 
            GameDeveloper(),
            GameValidator()
        ])
        
        # Set investment and run project
        team.invest(investment=3.0)
        team.run_project(content)
        
        # Run multi-agent collaboration  
        await team.run(n_round=n_rounds)
        
        # Get final results and save games
        final_results = team.env.memory.get(k=1)[0].content
        await self._save_games(final_results, output_dir)
        
        logger.info(f"🎉 Multi-agent generation complete!")

    async def _save_games(self, results_json: str, output_dir: str):
        """Save generated games to files"""
        try:
            results = json.loads(results_json)
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            successful_games = []
            for result in results:
                game_data = result.get("game_data", {})
                validation = result.get("validation", {})
                
                if validation.get("passes_validation", True):
                    # Save game file
                    title = game_data.get("title", f"Game {game_data.get('game_number', 1)}")
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    filename = f"game_{game_data.get('game_number', 1):02d}_{safe_title.replace(' ', '_')}.html"
                    
                    game_file = output_path / filename
                    with open(game_file, 'w', encoding='utf-8') as f:
                        f.write(game_data.get("html", ""))
                    
                    successful_games.append({
                        "title": title,
                        "filename": filename,
                        "validation_score": validation.get("validation_score", 0)
                    })
                    
                    logger.info(f"✅ Saved: {filename} (Score: {validation.get('validation_score', 0)}/10)")
            
            # Create index
            await self._create_index(successful_games, output_path)
            
        except Exception as e:
            logger.error(f"Error saving games: {str(e)}")

    async def _create_index(self, games: List[Dict], output_path: Path):
        """Create index page for all games"""
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Educational Games</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; text-align: center; }}
        .game-card {{ border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 15px 0; }}
        .game-title {{ font-size: 1.5em; font-weight: bold; color: #4CAF50; }}
        .game-score {{ color: #666; font-style: italic; }}
        button {{ background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #45a049; }}
    </style>
</head>
<body>
    <h1>🎮 Multi-Agent Educational Games</h1>
    <p>Generated using MetaGPT multi-agent collaboration</p>
    <p>Total games: {len(games)}</p>
"""
        
        for game in games:
            index_html += f"""
    <div class="game-card">
        <div class="game-title">{game['title']}</div>
        <div class="game-score">Quality Score: {game['validation_score']}/10</div>
        <button onclick="window.open('{game['filename']}', '_blank')">Play Game</button>
    </div>"""
        
        index_html += """
</body>
</html>"""
        
        index_file = output_path / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        logger.info(f"📄 Index page created: {index_file}")


async def main(
    content_file: str = "extract (1).txt",
    output_dir: str = "multi_agent_games", 
    n_rounds: int = 4
):
    """Main function to run multi-agent game generation"""
    system = MultiAgentGameSystem()
    await system.generate_educational_games(content_file, output_dir, n_rounds)


if __name__ == "__main__":
    import fire
    fire.Fire(main)