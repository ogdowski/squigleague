comments for current proposal and suggested changes:

Core
- lets keep only AoS data for now, with option to easily extend it to other systems

Squire
- Matchup functionality will be our main way to exchange army lists and randomize battle plans
- Top menu will have only two links: Matchup and Reference, matchup is default view for now under squigleague.com, which becomes my main gateway to app
- Add How It Works section to Matchup similar to one we have in Herald
- Use Herald-style link names for matchup (the ones passed to opponent), but even simpler (3 parts): adjective-noun-4_hex_characters, you can keep them exclusively age of sigmar / fantasy in vibe
- I actually prefer to generate link after first player passed their list, to avoid any suspicions
- when we submit list we no more have access to url we generated
- after we have both lists we want to have ability to pick a specific mission or to randomly select one - it doesnt matter which player will do it, but when it is done it cant be changed, we need there info if this was picked or randomly chosen, keep timestamp as well - all of it should be accesible under the same url until its deleted
- lets keep only Battle Plan name - without specific images for battle plans (their coming) this information is rarely useful. Images will come later so you can create placeholder for them in code
- Add information on minimium and maximum characters count for army list - lets keep it at 40 chars minimum and 10000 maximum
- lets keep 30 day removal clause, after which data is not avaialable under matchup url, but we will be able to access it for stats etc
- do not use browser prompts for copying data into clipboard, a little information popup which not require any action will be sufficient

Herald
- we want to remove herald functionality and use matchup instead, so remove it from app and views, but keep urls for backward compatibility, so people already exchanged their lists have an access for them untile they will be deleted
