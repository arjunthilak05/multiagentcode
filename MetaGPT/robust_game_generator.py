#!/usr/bin/env python3
"""
Robust Game Generator - Simplified version with better error handling
"""

import asyncio
import json
import re
import logging
from pathlib import Path
from metagpt.config2 import Config
from metagpt.actions.action import Action

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RobustCodeCleaner:
    """Robust code cleaner that doesn't fail on imperfect HTML"""
    
    @staticmethod
    def clean_html_response(raw_response: str) -> str:
        """Clean HTML response with maximum robustness"""
        try:
            cleaned = raw_response.strip()
            
            # Remove markdown wrappers aggressively
            patterns = [
                r'^```html\s*\n?',
                r'^```\s*\n?', 
                r'\n?```\s*$',
                r'```\s*$',
                r'^html\s*\n?'
            ]
            
            for pattern in patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
            
            cleaned = cleaned.strip()
            
            # If no DOCTYPE, add one
            if not cleaned.upper().startswith('<!DOCTYPE'):
                if '<html' in cleaned.lower():
                    cleaned = '<!DOCTYPE html>\n' + cleaned
                elif any(tag in cleaned.lower() for tag in ['<head>', '<body>', '<div>', '<script>']):
                    # Wrap incomplete HTML
                    cleaned = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Educational Game</title>
</head>
<body>
{cleaned}
</body>
</html>"""
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"HTML cleaning warning: {e}")
            # Return the best we can do
            return raw_response.strip()


class RobustGameGeneratorAction(Action):
    """Game generator that doesn't fail on HTML issues"""
    
    name: str = "RobustGameGeneratorAction"
    
    async def run(self, game_spec: dict) -> str:
        """Generate game with robust error handling"""
        
        prompt = f"""
Create a complete HTML5 educational game for Grade 6 students:

GAME: {game_spec.get('title', 'Educational Game')}
CONCEPT: {game_spec.get('concept', 'Learning concept')}
DIFFICULTY: {game_spec.get('difficulty', 'Medium')}

REQUIREMENTS:
- Single HTML file with embedded CSS and JavaScript
- Colorful, child-friendly design
- Interactive elements with click/touch
- Simple sound effects if possible
- Mobile-responsive
- Clear instructions

STRUCTURE:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_spec.get('title', 'Game')}</title>
    <style>
        /* CSS here */
    </style>
</head>
<body>
    <!-- Game content here -->
    <script>
        /* JavaScript here */
    </script>
</body>
</html>

Generate a complete, working game that teaches: {game_spec.get('concept', 'the learning concept')}

IMPORTANT: Return ONLY the HTML code, no explanations or markdown.
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
                        raise Exception("Generated HTML is too short")
                
                # Clean the HTML robustly
                cleaned_html = RobustCodeCleaner.clean_html_response(response)
                
                # Basic validation - but don't fail if it's not perfect
                if len(cleaned_html) < 200:
                    logger.warning(f"Cleaned HTML seems too short: {len(cleaned_html)} chars")
                    if attempt < max_retries - 1:
                        continue
                
                return cleaned_html
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed")
                    raise Exception(f"Failed to generate game after {max_retries} attempts")
                
                # Wait before retry
                await asyncio.sleep(1)
        
        raise Exception("All game generation attempts failed")
    


class RobustGameGenerator:
    """Simplified robust game generator"""
    
    def __init__(self, config_path: str = "config/config2.yaml"):
        self.config = Config.from_yaml_file(Path(config_path))
        logger.info(f"🤖 Robust Game Generator initialized with {self.config.llm.model}")
    
    async def generate_games_from_json(self, json_file: str = "progressive_game_system.json", output_dir: str = "robust_games"):
        """Generate games with maximum robustness"""
        
        logger.info(f"🚀 Starting robust game generation")
        
        try:
            # Load game specifications
            with open(json_file, 'r') as f:
                system_data = json.load(f)
            
            mini_games = system_data.get("mini_games", [])
            if not mini_games:
                logger.error("No games found in JSON file")
                return
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Generate each game
            generator_action = RobustGameGeneratorAction(llm_config=self.config.llm)
            successful_games = []
            
            for i, game_spec in enumerate(mini_games, 1):
                logger.info(f"🎮 Generating {i}/{len(mini_games)}: {game_spec.get('title', 'Untitled')}")
                
                try:
                    html_code = await generator_action.run(game_spec)
                    
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
                        "status": "success"
                    })
                    
                    logger.info(f"   ✅ Generated successfully: {filename}")
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to generate game {i}: {str(e)}")
            
            # Create simple index
            await self._create_simple_index(successful_games, output_path)
            
            logger.info(f"🎉 Generation complete! {len(successful_games)}/{len(mini_games)} games created")
            logger.info(f"📁 Files saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
    
    async def _create_simple_index(self, games, output_path):
        """Create a simple index page"""
        
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Educational Math Games</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ text-align: center; color: #333; }}
        .games {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .game {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
        .game h3 {{ color: #007bff; margin: 0 0 10px 0; }}
        .play-btn {{ background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
        .play-btn:hover {{ background: #218838; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Educational Math Games</h1>
        <p style="text-align: center;">Interactive games to learn mathematical patterns and shapes</p>
        
        <div class="games">
"""
        
        for game in games:
            index_html += f"""
            <div class="game">
                <h3>Game {game['number']}: {game['title']}</h3>
                <p>Learn about: {game['concept']}</p>
                <button class="play-btn" onclick="window.open('{game['filename']}', '_blank')">
                    🚀 Play Game
                </button>
            </div>
"""
        
        index_html += """
        </div>
    </div>
</body>
</html>"""
        
        index_file = output_path / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        logger.info(f"📄 Index page created: {index_file}")


async def main():
    """Main function"""
    generator = RobustGameGenerator()
    await generator.generate_games_from_json()


if __name__ == "__main__":
    asyncio.run(main())