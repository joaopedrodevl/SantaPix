
# SantaPix

É um app que faz integração com a API do banco Santander para geração de QrCode e Pix copia e cola. É necessário um certificado.pem cnpj e atualizar as variáveis de ambiente localizadas no compose.yml do backend.

Foi desenvolvido backend e frontend. O backend é uma API simples feita em python que comunica direto com a API do Banco, é nela que ficam as API_KEYS necessárias para gerar a chave de acesso de geração do pix.

No frontend foi usado JavaScript nativo, com HTML e CSS, criando um interface "amigável" para gerar o Pix QrCode.

Tanto o backend, quanto o frontend foram hospedados em uma máquina local usando docker. O frontend pode ser acessado em qualquer dispositivo: computadores, tablets e celulares, pois foi usado Apache Server para isso.
## Stack utilizada

**Front-end:** JavaScript, HTML e CSS

**Back-end:** Python e FastAPI
## Autores

- [@joaopedrodevl](https://www.github.com/joaopedrodevl)

