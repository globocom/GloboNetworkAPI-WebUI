GloboNetworkAPI Web UI 
======================

Esta ferramenta web ajuda os administradores de rede a gerenciar e automatizar 
recursos de rede (roteadores, switches e balanceadores de carga) e 
documentar a rede lógica e física.

Ela se baseia no
[GloboNetworkAPI](https://github.com/globocom/GloboNetworkAPI/), portanto, você precisa tê-lo instalado e 
acessível para usar a interface da web. Foram criados para serem independentes de fornecedores e para 
oferecer suporte a diferentes orquestradores e ambientes sem perder a visão 
centralizada de todos os recursos de rede alocados.

Não foi criado para ser um banco de dados de inventário, portanto, 
não possui funcionalidades de CMDB (gerenciamento de configuração de base de dados).


## Recursos

* Autenticação LDAP
* Suporta documentação de cabos (incluindo patch-panels/DIO's)
* Documentação separada para Camada 2 e Camada 3 (vlan/rede)
* Suporte para IPv4 e IPv6
* Alocação automática de Vlans, Redes e IPs
* Automação de ACL (lista de controle de acesso) (documentação/versionamento/aplicação)
* Suporte para Balanceadores de Carga
* Implantação automática de recursos alocados em switches, roteadores e balanceadores de carga
* Gerenciamento de balanceadores de carga
* Plugins expansíveis para automatizar a configuração

## Documentação
[Documentação](http://globonetworkapi-webui.readthedocs.org/en/latest/)

## Autores
[Autores](./AUTHORS.md)

*This article can also be read in [English](README.md).*
