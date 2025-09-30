#!/usr/bin/env python3
"""
Adaptive Game Generator - Dynamic content analysis and optimal game generation
"""

import asyncio
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from metagpt.config2 import Config
from metagpt.actions.action import Action

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdaptiveContentAnalyzer(Action):
    """Analyzes content complexity to determine optimal number of games"""
    
    name: str = "AdaptiveContentAnalyzer"
    
    async def run(self, content: str) -> Dict:
        """Analyze content and determine optimal game structure"""
        
        analysis_prompt = f"""
Analyze this educational content and determine the optimal number of interactive games needed to COMPLETELY teach this material.

CONTENT TO ANALYZE:
{content}

Your task is to:
1. Identify ALL distinct learning concepts that need separate games
2. Determine the complexity level of each concept  
3. Calculate how many games are needed for complete mastery
4. Ensure no concept is left untaught

ANALYSIS CRITERIA:
- Simple concepts (definitions, basic identification): 1 game
- Medium concepts (understanding relationships, patterns): 2-3 games  
- Complex concepts (application, creation, advanced patterns): 3-5 games
- Each distinct concept needs its own learning progression

REQUIREMENTS:
- Minimum 3 games (even for simple content)
- Maximum 15 games (to avoid overwhelming)
- Each game must teach something unique and essential
- Progressive difficulty from foundational to advanced
- Complete coverage - no gaps in learning

OUTPUT FORMAT (JSON):
{{
    "content_analysis": {{
        "total_concepts": number,
        "complexity_breakdown": {{
            "simple": number,
            "medium": number, 
            "complex": number
        }},
        "estimated_learning_time": "X minutes",
        "optimal_game_count": number,
        "reasoning": "Why this number of games is perfect for this content"
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

IMPORTANT: Return ONLY valid JSON, no explanations.
"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.llm.aask(analysis_prompt)
                
                # Clean and parse JSON
                cleaned_response = self._clean_json_response(response)
                analysis_data = json.loads(cleaned_response)
                
                # Validate the analysis
                if self._validate_analysis(analysis_data):
                    logger.info(f"✅ Content analysis complete: {analysis_data['content_analysis']['optimal_game_count']} games recommended")
                    return analysis_data
                else:
                    logger.warning(f"Analysis validation failed on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"Analysis attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to analyze content after {max_retries} attempts")
                await asyncio.sleep(1)
        
        raise Exception("All content analysis attempts failed")
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from markdown and other formatting"""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        patterns = [
            r'^```json\s*\n?',
            r'^```\s*\n?',
            r'\n?```\s*$',
            r'```\s*$'
        ]
        
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        return cleaned.strip()
    
    def _validate_analysis(self, data: Dict) -> bool:
        """Validate the analysis structure"""
        try:
            required_keys = ['content_analysis', 'game_specifications']
            if not all(key in data for key in required_keys):
                return False
            
            content_analysis = data['content_analysis']
            if 'optimal_game_count' not in content_analysis:
                return False
            
            game_count = content_analysis['optimal_game_count']
            if not (3 <= game_count <= 15):
                return False
            
            games = data['game_specifications']
            if len(games) != game_count:
                return False
            
            return True
            
        except Exception:
            return False
    


class EnhancedGameGenerator(Action):
    """Enhanced game generator with perfect educational design"""
    
    name: str = "EnhancedGameGenerator"
    
    async def run(self, game_spec: dict, total_games: int, game_position: int) -> str:
        """Generate enhanced educational game with context awareness"""
        
        # Enhanced prompt with context awareness
        prompt = f"""
Create a PERFECT HTML5 educational game for Grade 6 students.

GAME CONTEXT:
- This is game {game_position} of {total_games} in a learning sequence
- Title: {game_spec.get('title', 'Educational Game')}
- Concept: {game_spec.get('concept', 'Learning concept')}
- Difficulty: {game_spec.get('difficulty', 'Medium')}
- Learning Objective: {game_spec.get('learning_objective', 'Educational goal')}
- Prerequisites: {game_spec.get('prerequisites', [])}
- Builds Toward: {game_spec.get('builds_toward', [])}

EDUCATIONAL REQUIREMENTS:
- Perfect pedagogical design for the specific concept
- Progressive difficulty appropriate for position in sequence
- Clear learning objectives and success criteria
- Immediate feedback and positive reinforcement
- Multiple interaction types to engage different learning styles
- Assessment built into gameplay

TECHNICAL REQUIREMENTS:
- Single HTML file with embedded CSS and JavaScript
- Mobile-responsive design (works on phones and tablets)
- Accessible design (WCAG guidelines)
- Engaging animations and transitions
- Sound effects for feedback
- Clean, child-friendly UI
- Error handling and graceful degradation

GAME STRUCTURE:
- Welcome screen with clear instructions
- Progressive levels or challenges
- Real-time feedback system
- Success celebrations
- Optional replay functionality
- Progress indicators

IMPORTANT DESIGN PRINCIPLES:
- Make it FUN and engaging
- Clear visual hierarchy
- Intuitive controls
- Immediate response to actions
- Celebrate small wins
- Build confidence progressively

Generate a complete, working game that PERFECTLY teaches: {game_spec.get('concept', 'the learning concept')}

Return ONLY the complete HTML code with embedded CSS and JavaScript.
"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.llm.aask(prompt)
                
                if not response or len(response.strip()) < 100:
                    logger.warning(f"Short response on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return self._create_enhanced_fallback(game_spec)
                
                # Clean the HTML
                from fixed_code_cleaner import FixedCodeCleaner
                cleaned_html = FixedCodeCleaner.clean_html_response(response)
                
                if len(cleaned_html) < 200:
                    logger.warning(f"Cleaned HTML too short: {len(cleaned_html)} chars")
                    if attempt < max_retries - 1:
                        continue
                
                return cleaned_html
                
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate game after {max_retries} attempts")
                await asyncio.sleep(1)
        
        raise Exception("All game generation attempts failed")
    


class AdaptiveGameSystem:
    """Complete adaptive game generation system"""
    
    def __init__(self, config_path: str = "config/config2.yaml"):
        self.config = Config.from_yaml_file(Path(config_path))
        logger.info(f"🤖 Adaptive Game System initialized with {self.config.llm.model}")
    
    async def generate_adaptive_games(self, content_file: str = "extract (1).txt", output_dir: str = "adaptive_games"):
        """Generate optimal number of games based on content analysis"""
        
        logger.info(f"🚀 Starting adaptive game generation")
        
        try:
            # Stage 1: Load and validate content
            logger.info("📖 Stage 1: Loading content")
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 50:
                logger.error("Content too short for analysis")
                return
            
            # Stage 2: Adaptive content analysis
            logger.info("🔍 Stage 2: Analyzing content complexity")
            analyzer = AdaptiveContentAnalyzer(llm_config=self.config.llm)
            analysis = await analyzer.run(content)
            
            optimal_games = analysis['content_analysis']['optimal_game_count']
            logger.info(f"📊 Analysis complete: {optimal_games} games recommended")
            logger.info(f"🕒 Estimated learning time: {analysis['content_analysis']['estimated_learning_time']}")
            
            # Stage 3: Create output directory
            logger.info("📁 Stage 3: Setting up output directory")
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Stage 4-7: Generate each game with enhanced system
            logger.info(f"🎮 Stage 4-7: Generating {optimal_games} adaptive games")
            generator = EnhancedGameGenerator(llm_config=self.config.llm)
            successful_games = []
            
            for i, game_spec in enumerate(analysis['game_specifications'], 1):
                logger.info(f"   🎯 Generating {i}/{optimal_games}: {game_spec.get('title', 'Untitled')}")
                
                try:
                    html_code = await generator.run(game_spec, optimal_games, i)
                    
                    # Save the game
                    title = game_spec.get('title', f'Game {i}')
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    filename = f"game_{i:02d}_{safe_title.replace(' ', '_')}.html"
                    game_file = output_path / filename
                    
                    with open(game_file, 'w', encoding='utf-8') as f:
                        f.write(html_code)
                    
                    successful_games.append({
                        "number": i,
                        "title": title,
                        "filename": filename,
                        "concept": game_spec.get('concept', 'Learning'),
                        "difficulty": game_spec.get('difficulty', 'Medium'),
                        "learning_objective": game_spec.get('learning_objective', 'Educational goal'),
                        "estimated_time": game_spec.get('estimated_time', '3 minutes'),
                        "status": "success"
                    })
                    
                    logger.info(f"     ✅ Generated successfully: {filename}")
                    
                except Exception as e:
                    logger.error(f"     ❌ Failed to generate game {i}: {str(e)}")
            
            # Stage 8: Create enhanced index and reports
            logger.info("📄 Stage 8: Creating index and reports")
            await self._create_enhanced_index(successful_games, analysis, output_path)
            await self._save_analysis_report(analysis, successful_games, output_path)
            
            logger.info(f"🎉 Adaptive generation complete!")
            logger.info(f"📊 Generated {len(successful_games)}/{optimal_games} games")
            logger.info(f"📁 Files saved to: {output_path}")
            logger.info(f"🎯 Perfectly adapted to content complexity!")
            
        except Exception as e:
            logger.error(f"Critical error in adaptive system: {str(e)}")
    
    async def _create_enhanced_index(self, games, analysis, output_path):
        """Create enhanced index page with learning analytics"""
        
        total_time = sum(int(game.get('estimated_time', '3').split()[0]) for game in games)
        game_count = len(games)
        
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adaptive Educational Games - Perfect Learning Experience</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .header {{
            background: rgba(255,255,255,0.95);
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 15px 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        .games-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        .game-card {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .game-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        .game-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .game-number {{
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }}
        .game-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        .game-details {{
            margin: 15px 0;
        }}
        .detail-item {{
            margin: 8px 0;
            display: flex;
            align-items: center;
        }}
        .detail-icon {{
            margin-right: 10px;
            font-size: 1.1em;
        }}
        .difficulty {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: auto;
        }}
        .difficulty.very-easy {{ background: #e8f5e8; color: #2e7d32; }}
        .difficulty.easy {{ background: #e3f2fd; color: #1565c0; }}
        .difficulty.medium {{ background: #fff3e0; color: #ef6c00; }}
        .difficulty.hard {{ background: #fce4ec; color: #c2185b; }}
        .difficulty.very-hard {{ background: #f3e5f5; color: #7b1fa2; }}
        .play-btn {{
            width: 100%;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 15px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 15px;
        }}
        .play-btn:hover {{
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .analysis-section {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 25px;
            margin: 30px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        @media (max-width: 768px) {{
            .games-grid {{
                grid-template-columns: 1fr;
            }}
            .stats {{
                flex-direction: column;
                align-items: center;
            }}
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 Adaptive Educational Games</h1>
        <p>Perfectly designed learning experience based on content analysis</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{game_count}</div>
                <div class="stat-label">Perfect Games</div>
            </div>
            <div class="stat">
                <div class="stat-number">{total_time}</div>
                <div class="stat-label">Minutes of Learning</div>
            </div>
            <div class="stat">
                <div class="stat-number">{analysis['content_analysis']['total_concepts']}</div>
                <div class="stat-label">Concepts Covered</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="analysis-section">
            <h2>🔍 Content Analysis Results</h2>
            <p><strong>Reasoning:</strong> {analysis['content_analysis']['reasoning']}</p>
            <p><strong>Complexity Breakdown:</strong></p>
            <ul>
                <li>Simple concepts: {analysis['content_analysis']['complexity_breakdown']['simple']}</li>
                <li>Medium concepts: {analysis['content_analysis']['complexity_breakdown']['medium']}</li>
                <li>Complex concepts: {analysis['content_analysis']['complexity_breakdown']['complex']}</li>
            </ul>
        </div>
        
        <div class="games-grid">"""
        
        for game in games:
            difficulty_class = game['difficulty'].lower().replace(' ', '-')
            index_html += f"""
            <div class="game-card">
                <div class="game-header">
                    <div class="game-number">{game['number']}</div>
                    <div class="game-title">{game['title']}</div>
                    <div class="difficulty {difficulty_class}">{game['difficulty']}</div>
                </div>
                
                <div class="game-details">
                    <div class="detail-item">
                        <span class="detail-icon">🎯</span>
                        <span><strong>Concept:</strong> {game['concept']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-icon">📚</span>
                        <span><strong>Objective:</strong> {game['learning_objective']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-icon">⏱️</span>
                        <span><strong>Time:</strong> {game['estimated_time']}</span>
                    </div>
                </div>
                
                <button class="play-btn" onclick="window.open('{game['filename']}', '_blank')">
                    🚀 Start Learning
                </button>
            </div>"""
        
        index_html += """
        </div>
    </div>
</body>
</html>"""
        
        index_file = output_path / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        logger.info(f"📄 Enhanced index page created: {index_file}")
    
    async def _save_analysis_report(self, analysis, games, output_path):
        """Save detailed analysis report"""
        report = {
            "analysis_metadata": {
                "timestamp": "2025-09-30",
                "system_version": "Adaptive Game Generator v1.0",
                "analysis_type": "content_complexity_assessment"
            },
            "content_analysis": analysis['content_analysis'],
            "generated_games": games,
            "system_performance": {
                "total_games_requested": analysis['content_analysis']['optimal_game_count'],
                "total_games_generated": len(games),
                "success_rate": f"{(len(games) / analysis['content_analysis']['optimal_game_count']) * 100:.1f}%"
            }
        }
        
        report_file = output_path / "analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Analysis report saved: {report_file}")


async def main():
    """Main function"""
    system = AdaptiveGameSystem()
    await system.generate_adaptive_games()


if __name__ == "__main__":
    asyncio.run(main())