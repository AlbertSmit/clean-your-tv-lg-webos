# Clean Your TV — guia de uso

No-root e Root são opções equivalentes para diferentes configurações da TV. Escolha No-root para LG Developer Mode ou Root se já tiver acesso root por SSH. A compatibilidade e os testes realizados são específicos de cada edição.

## Requisitos

Este guia cobre instalação, uso e recuperação. A escolha de idioma e o aplicativo para macOS/Linux estão incluídos na [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3). Os downloads antigos da v0.9.0 não incluem o aplicativo gráfico. Consulte a [instalação das duas edições](../INSTALL.md).

Ligue a TV e conecte os dois dispositivos à mesma rede local confiável. Depois, o computador pode ficar desligado. A compatibilidade depende do modelo, firmware e controle remoto; Root ainda tem testes em hardware pendentes.

- **No-root:** ative LG Developer Mode e Key Server. Digite a frase de acesso exibida na TV e aceite nela o pedido separado de pareamento. Developer Mode deve continuar ativo: a expiração pode remover aplicativos instalados por esse método. Confira o cronômetro oficial mesmo com a renovação Beta ativada. O monitoramento do Helper depende da rede local.
- **Root:** é necessário acesso SSH root já existente. O instalador não faz root. Não ative Developer Mode em uma TV que já tenha root. Mantenha o acesso root e os serviços de recuperação disponíveis.

## Instalação e idioma

- **Windows x64:** baixe `cytv-windows-x64-desktop.zip`, escolha **Extrair tudo** no Explorador de Arquivos e abra `cytv-desktop/cytv-desktop.exe`. Mantenha a pasta `_internal` ao lado. A assinatura de editor do Windows não está configurada. O console separado é `cytv-windows-x64.exe`; renomeie para `cytv.exe` e use `.\cytv.exe` no PowerShell para os comandos abaixo.
- **macOS 13+:** extraia `cytv-macos-arm64.zip` para Apple Silicon ou `cytv-macos-x64.zip` para Intel; mova `cytv.app` para Aplicativos e abra. Permita acesso à rede local. Se uma cópia confiável for bloqueada, use Privacidade e Segurança → Abrir Mesmo Assim; não desative o Gatekeeper. A compatibilidade com sistemas antigos não foi confirmada.
- **Linux x64:** no Ubuntu 22.04+, Debian 12+ ou Mint 21+, instale `cytv-linux-x64.deb` com o gerenciador gráfico de pacotes e abra Clean Your TV pelo menu. Pode ser necessário acesso à Internet para bibliotecas. Não há pacote Linux ARM. O executável independente `cytv-linux-x64` é a CLI; use o `.deb` para o app gráfico.

[Instalador Android](../../android/README.md): inclui os dez idiomas da interface. O controle no canto superior direito mostra o idioma atual; toque para escolher outro. A seleção fica salva no telefone.

O assistente usa inicialmente o idioma do sistema e salva sua escolha explícita. Na TV, abra **Configurações → Idioma** e escolha um idioma ou a opção automática do sistema. As preferências da TV e do instalador são independentes. Veja os códigos no [índice de idiomas](../LANGUAGES.md).

Para a CLI baixada separadamente no macOS/Linux, na pasta extraída:

```sh
chmod +x cytv
./cytv --language pt-BR install
```

Escolha a TV ou informe o IP, selecione a edição e confira o resumo. Confirme uma nova identidade SSH apenas para sua TV em uma rede confiável; uma chave salva que mudou bloqueia o acesso. Root prepara a recuperação e ativa Home imediatamente, sem período de teste nem etapa de confirmação para manter. Teste setas, OK, Home, Voltar/Cancelar, volume, espera e inicialização a frio.

## Uso e recuperação

Setas selecionam; OK abre; segure OK para reorganizar. Um toque em Voltar mantém a navegação e a confirmação de saída do aplicativo. Home abre o lançador com o controle ativo. Nas novas compilações, segure Voltar por 1,2 segundos para abrir LG Home uma vez. O interruptor de controle do Home e suas configurações não mudam.

**Novas compilações: pressione Home três vezes em dois segundos**, soltando entre os toques. Isso restaura LG Home e interrompe o controle sem apagar preferências. No No-root Helper até a versão 0.6.13, segure Home por cerca de dois segundos. Segurar Home não é o gesto de emergência do Root.

No-root: abra **Home Helper** na lista de aplicativos LG para retomar; abrir apenas Home não remove a parada. Root: ative **Alterar Home** nas configurações do Home para retomar. **Abrir LG Home** abre LG Home uma vez sem mudar o destino de Home. Para restaurar LG Home como destino permanente, desative **Alterar Home** ou execute `cytv restore`. Nunca execute os dois controladores juntos. Se a falha voltar, mantenha LG Home ativo.

```sh
./cytv --language pt-BR status
./cytv --language pt-BR doctor --report
./cytv --language pt-BR restore
./cytv --language pt-BR uninstall
```

Após uma interrupção, execute primeiro `status` e preserve os registros. `restore` restaura LG Home sem remover aplicativos; `uninstall` restaura antes de remover. Os dados de recuperação Root são mantidos de propósito: não os apague para forçar a reinstalação. Revise relatórios antes de compartilhar; não publique chaves nem pastas de perfis.

## Atualização e remoção

Guarde pacotes funcionais e cópias privadas das configurações. Pare No-root Helper antes de substituir pacotes; atualize pelo computador sem desinstalar antes, pois isso pode apagar preferências. A instalação combinada Root pelo cytv inclui atualização de versões compatíveis em Configurações → Atualizações de software; a instalação manual tem outras limitações. Não substitua uma instalação Root ativa por uma IPK avulsa. Use o processo explícito de reinstalação do cytv. Remover o aplicativo do computador não remove os aplicativos da TV.

Documentação técnica em inglês: [aplicativo de computador](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [instalação manual](../MANUAL_INSTALL.md), [recuperação](../RECOVERY.md), [edições](../EDITIONS.md).

Após conectar, o cytv lê as versões na TV e mostra a versão atual → incluída para Home e Home Helper (No-root), ou Root e Root Updater. Revise e confirme antes de instalar. Primeira instalação, reinstalação e instalação de versão anterior são identificadas; `--yes` pula a confirmação, mas exibe as versões.

Atualizações de software mostra detalhes apenas da versão instalada ou mais recente. Abra Recuperação para ver a versão salva para restaurar ou por que a reversão está indisponível; Voltar retorna às atualizações.

No-root verifica a ABI do shell da TV e aceita um kernel de 64 bits com ambiente ARM32 confirmado. Se a verificação falhar, anexe o JSON de diagnóstico gerado; não compartilhe chaves ou frases secretas.

As atualizações do Home pedem confirmação antes da instalação; depois a inicialização é verificada automaticamente. A atualização de status mantém o botão selecionado pelo controle.

No Root e no No-root, a inicialização é confirmada automaticamente após a instalação; não é preciso confirmar que tudo funciona. A reversão continua disponível após a confirmação, sem limite de tempo, até a próxima atualização. Ela restaura a versão anterior do Home e as configurações salvas antes da atualização; alterações posteriores podem ser perdidas. Um aviso aparece antes de iniciar a reversão. Atualizações e reversões do No-root na TV ainda exigem root e Homebrew Channel; caso contrário, use o instalador no computador.

A tela de atualização separa versões, estado e novidades legíveis. Cima/Baixo percorre as notas; Esquerda/Direita seleciona as ações fixas abaixo. Após a verificação automática de inicialização, o Root restaura o controle do Home se estava ligado; o No-root preserva o estado do Helper separado. Preferências desligadas e desativação explícita ou de emergência permanecem desligadas.

Ao abrir as configurações do Home, as atualizações são verificadas em segundo plano. Um ponto laranja em Atualizações de software indica uma versão mais recente, inclusive quando exige instalação pelo computador. As configurações continuam disponíveis durante a verificação.

No-root: abra Configurações do Home → Modo de Desenvolvedor para renovação automática, verificação de sessão e diagnóstico. A tela principal mantém um resumo do estado e os erros de renovação visíveis. Voltar retorna às configurações do Home. As duas edições colocam Idioma, Atualizações de software e Configurações da TV na mesma linha; a seta abre cada item.
