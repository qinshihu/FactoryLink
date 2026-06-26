# Gateway de Aquisição de Dados Industriais v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[中文](./README.md) | [English](./README.en.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md) | [Español](./README.es.md) | [Русский](./README.ru.md)

## O que é isto?

Um **gateway de aquisição de dados industriais** em um **único EXE, duplo clique para executar, zero dependências, completamente open-source e gratuito**.

Projetado para engenheiros de chão de fábrica, equipe de TI de fábrica e pequenos integradores de sistemas na indústria de manufatura.

## Por que criar isto?

- Gateways comerciais custam mais de €1.000 por unidade — criamos um gratuito para todos
- Outros projetos open-source exigem Docker, que os engenheiros de chão de fábrica não sabem usar
- A maioria dos projetos internacionais não tem documentação em chinês, dificultando a resolução de problemas

## Como usar?

1. [Baixar `FactoryLink.exe`](https://github.com/qinshihu/FactoryLink/releases/latest)

2. Clique duas vezes para executar (um ícone aparecerá na bandeja do sistema no canto inferior direito)

![Ícone da bandeja](images/1(2).png)

3. O navegador abrirá automaticamente a página de configuração (padrão `http://localhost:8000`)

![Página de configuração](images/1(1).png)

4. Configure o IP do seu PLC, tabela de pontos e endereço MQTT

![Configuração do dispositivo](images/1(4).png)

5. Clique em "Iniciar aquisição" — pronto!

> Clique com o botão direito no ícone da bandeja para: abrir página de configuração, iniciar/parar aquisição, sair do programa.
> 
> A implantação via Docker também é suportada: [Guia de implantação Docker](#implantação-docker)

## Protocolos suportados

| Protocolo | Modelos suportados | Biblioteca |
|-----------|-------------------|------------|
| Modbus TCP | Todos os dispositivos Modbus TCP padrão | pymodbus 3.x |
| Modbus RTU | Todos os dispositivos Modbus RTU padrão (serial) | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0 (Python puro) |
| Mitsubishi MC | FX5U / Série Q / Série L | pymcprotocol |

## Funcionalidades principais

- **EXE único**: Duplo clique para executar, sem necessidade de ambiente de execução
- **Interface Web**: Configuração via navegador, sem conhecimento de linha de comando
- **Dados em tempo real**: Push via WebSocket, dados atualizados em tempo real
- **Encaminhamento MQTT**: Encaminhamento automático dos dados coletados para o servidor MQTT
- **Importação Excel**: Importação em lote de configurações de pontos a partir de planilhas Excel com diálogo de pré-visualização
- **Assistente IA**: Descreva seu dispositivo em linguagem natural, a IA gera automaticamente a configuração (compatível com OpenAI / Qwen / DeepSeek, streaming SSE + pré-visualização editável)
- **Teste de conexão**: Teste de conectividade do PLC com um clique
- **Reconexão automática**: Reconexão automática em caso de perda de rede com backoff exponencial
- **Inicialização automática**: Configuração de inicialização do Windows com um clique
- **Bandeja do sistema**: Execução em segundo plano, clique direito no ícone para operações
- **Visualizador de logs**: Visualização de logs de aquisição diretamente na interface web com filtragem por nível
- **Recarga a quente**: Clique em "Aplicar" após alterações de configuração para reiniciar automaticamente o coletor
- **Backup automático**: Geração automática de `config.json.bak` a cada salvamento
- **Tratamento de conflito de porta**: Troca automática para 8001, 8002... se a porta 8000 estiver ocupada

## Visão geral da interface

| Página | Funções |
|--------|---------|
| **Início** | Lista de cartões de dispositivos, exibição de dados em tempo real, botão iniciar/parar, status online dos dispositivos, status de conexão MQTT |
| **Config. Dispositivo** | Adicionar/editar/excluir dispositivos, configuração por protocolo, CRUD da tabela de pontos, importação Excel (pré-visualização)/download de modelo, teste de conexão, **Assistente IA** (linguagem natural para configuração) |
| **Config. Sistema** | Configuração MQTT, intervalo de coleta, estratégia de reconexão, inicialização automática, **Config. IA** (URL API/Chave/Modelo), visualizador de logs (filtragem por nível) |

## Formato dos dados

### Tópico de dados MQTT

```
{topic_prefix}/{device_id}
```

Exemplo: `factory/gateway-001/dev1`

### Carga útil MQTT

```json
{
  "gateway": "Gateway Oficina 1",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "Temperatura1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "Pressão1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### Tópico de status

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "Conexão bem-sucedida",
  "timestamp": 1719123456789
}
```

- Valores de status: `online` (aquisição normal), `offline` (desconectado), `error` (anormal)
- Valores de quality: `good` (normal), `bad` (falha na leitura), `uncertain` (dados suspeitos)

## Tipos de dados dos pontos

| Tipo | Descrição | Bytes |
|------|-----------|-------|
| bool | Booleano | 1 bit |
| int16 | Inteiro com sinal de 16 bits | 2 |
| uint16 | Inteiro sem sinal de 16 bits | 2 |
| int32 | Inteiro com sinal de 32 bits | 4 |
| uint32 | Inteiro sem sinal de 32 bits | 4 |
| float | Ponto flutuante de 32 bits | 4 |
| double | Ponto flutuante de 64 bits | 8 |

> Valor real = Valor bruto × Taxa + Deslocamento. A taxa e o deslocamento são configurados nas definições do ponto.

## Arquivo de configuração

Toda a configuração é salva em `config.json` no mesmo diretório do EXE, com backup automático em `config.json.bak` a cada alteração.

```json
{
  "gateway_name": "Gateway Oficina 1",
  "devices": [
    {
      "id": "dev1",
      "name": "Siemens S7-1200",
      "protocol": "s7",
      "ip": "192.168.1.100",
      "rack": 0,
      "slot": 1,
      "enabled": true,
      "points": [
        {"name": "Temperatura1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
      ]
    }
  ],
  "mqtt": {
    "host": "192.168.1.200",
    "port": 1883,
    "client_id": "gateway-001",
    "topic_prefix": "factory/gateway-001",
    "username": "",
    "password": "",
    "qos": 1,
    "enabled": true
  },
  "collect_interval": 1000,
  "reconnect": {
    "max_retries": 0,
    "base_delay": 1,
    "max_delay": 60
  },
  "ai": {
    "enabled": false,
    "api_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-3.5-turbo"
  }
}
```

- `collect_interval`: Intervalo de coleta em milissegundos, 1000 = uma vez por segundo
- `reconnect.max_retries`: 0 = tentativas ilimitadas
- Intervalo de repetição: backoff exponencial, 1s → 2s → 4s → 8s → 16s → 32s → 60s (limite)

## Formatos de endereço dos protocolos

### Modbus

| Faixa de endereços | Área | Exemplo |
|-------------------|------|---------|
| 40001-49999 | Registradores de retenção | `40001` |
| 30001-39999 | Registradores de entrada | `30001` |
| 10001-19999 | Entradas discretas | `10001` |
| 00001-09999 | Bobinas | `00001` |

### Siemens S7

| Formato | Descrição | Exemplo |
|---------|-----------|---------|
| DBx.DBDy | Palavra dupla do bloco DB (32 bits) | `DB1.DBD0` |
| DBx.DBXy.z | Bit do bloco DB | `DB1.DBX8.0` |
| DBx.DBWy | Palavra do bloco DB (16 bits) | `DB1.DBW0` |
| Mx.y | Bit de memória | `M0.0` |
| Ix.y | Bit de entrada | `I0.0` |
| Qx.y | Bit de saída | `Q0.0` |

> S7-1200/1500: rack=0, slot=1; S7-300/400: rack=0, slot=2

### Mitsubishi MC

| Formato | Descrição | Exemplo |
|---------|-----------|---------|
| Dxxxx | Registrador de dados | `D100` |
| Mxxxx | Relé interno | `M100` |
| Xx | Relé de entrada | `X0` |
| Yx | Relé de saída | `Y0` |
| Wxxxx | Registrador de link | `W100` |

## Formato da tabela Excel de pontos

| Nome do ponto | Endereço | Tipo de dado | Taxa | Deslocamento | Unidade |
|--------------|----------|-------------|------|-------------|---------|
| Temperatura1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| Pressão1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| Status operação | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- A primeira linha é o cabeçalho (formato fixo), os dados começam na linha 2
- Suporta os formatos `.xlsx` e `.xls`
- Baixe o modelo na página de configuração do dispositivo

## Executar a partir do código fonte

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependências Python
pip install -r requirements.txt

# 3. Compilar o frontend
cd frontend
npm install
npm run build
cd ..

# 4. Iniciar o backend
cd backend
python main.py
```

Abra `http://localhost:8000` no seu navegador.

## Compilar para EXE

```bash
# Certifique-se de que o frontend está compilado
cd frontend && npm run build && cd ..

# Executar script de compilação
build.bat
```

Saída: `dist/FactoryLink.exe` (~25 MB)

## Implantação Docker

Se preferir não usar o EXE, pode executar com Docker (adequado para servidores, PCs industriais, Raspberry Pi).

### Início rápido

```bash
# Baixar imagem
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# Criar diretórios para configuração e logs
mkdir -p /opt/factorylink/{logs,config}

# Executar contêiner
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### Referência de parâmetros

| Parâmetro | Descrição |
|-----------|-----------|
| `-p 8000:8000` | Mapear porta da página de configuração web |
| `-v /opt/factorylink/config:/app/config` | Montar diretório de configuração (config.json salvo aqui) |
| `-v /opt/factorylink/logs:/app/logs` | Montar diretório de logs |
| `--restart always` | Reinicialização automática em caso de falha do contêiner |

### Primeira utilização

1. Após iniciar o contêiner, abra `http://ip-do-seu-servidor:8000` no navegador
2. Configure os dispositivos PLC e MQTT
3. Clique em "Iniciar aquisição"

> Nota: A versão Docker **não suporta** o ícone da bandeja do sistema e a inicialização automática (funcionalidades exclusivas do Windows).

### Usar docker-compose

Crie `docker-compose.yml`:

```yaml
version: '3'
services:
  factorylink:
    image: registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
    container_name: factorylink
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
```

Iniciar:

```bash
docker-compose up -d
```

## Stack tecnológico

- **Backend**: Python 3.11+ / FastAPI / WebSocket / uvicorn
- **Frontend**: Vue 3 / Vite / Element Plus / xlsx
- **Bibliotecas de protocolo**: pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**: paho-mqtt
- **Empacotamento**: PyInstaller 6.x (`--onefile --windowed`)
- **Bandeja do sistema**: pystray + Pillow

## Estrutura do projeto

```
FactoryLink/
├── backend/
│   ├── main.py              # Ponto de entrada FastAPI (WebSocket, bandeja, detecção de porta)
│   ├── config.py            # Gerenciamento de configuração (leitura/escrita, backup, thread-safe)
│   ├── logger.py            # Gerenciamento de logs (rotação 10 MB × 5, leitura via API)
│   ├── schemas.py           # Modelos de dados Pydantic
│   ├── collector/
│   │   ├── base.py          # Classe base do coletor (reconexão com backoff exponencial, thread de reconexão)
│   │   ├── modbus.py        # Modbus TCP/RTU (pymodbus)
│   │   ├── s7.py            # Siemens S7 (python-snap7 3.0)
│   │   └── mitsubishi.py    # Mitsubishi MC (pymcprotocol)
│   └── forwarder/
│       └── mqtt.py          # Encaminhamento MQTT (paho-mqtt)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Framework de layout (navegação, logo, informações do autor)
│   │   ├── router.js        # Configuração de rotas
│   │   └── views/
│   │       ├── Home.vue          # Página inicial (cartões de dispositivos, dados em tempo real, WebSocket)
│   │       ├── DeviceConfig.vue  # Configuração de dispositivo (CRUD, gerenciamento de pontos, importação Excel)
│   │       └── Settings.vue      # Configurações do sistema (MQTT, coleta, reconexão, inicialização auto, logs)
│   └── dist/                # Arquivos estáticos compilados
├── build.bat                # Script de compilação PyInstaller
├── requirements.txt         # Lista de dependências Python
├── Dockerfile               # Imagem Docker
└── README.md                # Este arquivo
```

## Perguntas frequentes

**P: Nada acontece ao clicar duas vezes no EXE?**

R: Verifique a bandeja do sistema no canto inferior direito para ver o ícone do gateway. Se a porta estiver ocupada, o programa trocará automaticamente de porta. Clique com o botão direito no ícone e selecione "Abrir página de configuração".

**P: Não é possível conectar ao PLC?**

R: Primeiro clique em "Testar conexão" na página de configuração do dispositivo para verificar IP, porta, números de rack/slot. Siemens S7-1200/1500 usa rack=0, slot=1; S7-300/400 usa rack=0, slot=2.

**P: MQTT não recebe dados?**

R: Verifique se o endereço e a porta do servidor MQTT estão corretos e se o MQTT está habilitado. Consulte os logs na página de configurações do sistema para diagnosticar erros de conexão.

**P: Como importar pontos em lote?**

R: Baixe o modelo Excel na página de configuração do dispositivo, preencha-o e importe. O cabeçalho é fixo: Nome do ponto, Endereço, Tipo de dado, Taxa, Deslocamento, Unidade.

**P: Como configurar a porta serial Modbus RTU?**

R: Insira o nome da porta diretamente, por exemplo `COM3`, `COM4`. A taxa de transmissão padrão é 9600, a paridade padrão é Nenhuma (N).

**P: Qual é o intervalo de coleta ideal?**

R: O padrão é 1000 ms (1 segundo). Para PLCs rápidos, 500 ms é possível. Para dispositivos mais lentos, recomenda-se 2000 ms+. Um intervalo muito curto pode causar timeouts de leitura.

---

Porque 90% dos engenheiros de chão de fábrica não precisam de cloud-native ou Docker — eles só querem uma ferramenta simples e fácil de usar que resolva o problema.

---

## Licença

Este projeto é open-source sob a licença **Mozilla Public License 2.0 (MPL-2.0)**.

## Autor

**Tan Ce** — Desenvolvedor independente | Explorador de IoT industrial

- 📝 Blog: [https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 Email: huawei_network@foxmail.com
- 💬 Conta oficial do WeChat: **IT Online**

![QR Code WeChat](images/公众号背面.png)

---

[MPL-2.0](./LICENSE) © Tan Ce
