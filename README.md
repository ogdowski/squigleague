# Squig League

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Open-source Warhammer management platform with integrated modules for fair play, tournament organization, and collection management.

**Live:** [squigleague.com](https://squigleague.com)

## Architecture

Squig League uses a modern frontend/backend separation architecture:

- **Backend** (herald/): FastAPI JSON API serving `/api/herald/*` endpoints
- **Frontend** (frontend/): Alpine.js SPA serving static UI
- **Nginx**: Routes `/api/*` to backend, everything else to frontend
- **Database**: PostgreSQL (shared by all modules)

This architecture enables independent scaling, easier testing, and clean separation of concerns.

## Modules

### Active

- **Herald** - Blind army list exchange for fair battles

### Roadmap

- **Herald**: Mission randomizer (AoS and 40k) - hardcoded until we integrate with BS Data
- **Archivist**: BSData integration
- **Herald**: Mission randomizer using BSData
- **Squire**: Score tracker and battle assistant
- **Marshal**: Army builder
- **Keeper**: Personal army tracker
- **Patron**: Tournament management system
- **Archivist**: Rules and unit viewer

## Getting Started

See [SETUP.md](SETUP.md) for installation and setup instructions.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Code of Conduct:** Be respectful and professional. We follow the [Contributor Covenant](https://www.contributor-covenant.org).

**Security:** Found a vulnerability? Email **squigleague@proton.me** - don't create public issues.

**Questions?** Open an [issue](https://github.com/arielogdowski/squig_league/issues) or email squigleague@proton.me

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

Copyright © 2025 Ariel Ogdowski

## Disclaimer

Squig League is an independent project and is not affiliated with, endorsed by, or associated with Games Workshop Limited. All Warhammer-related trademarks and copyrights are property of Games Workshop Limited.
