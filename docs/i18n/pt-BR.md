# Clean Your TV — guia de uso

No-root e Root são opções equivalentes para diferentes configurações da TV. Escolha No-root para LG Developer Mode ou Root se já tiver acesso root por SSH. A compatibilidade e os testes realizados são específicos de cada edição.

## Requisitos

Este guia descreve **[v1.3.0 estável](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0)**. Os links `releases/latest/download` entregam a versão estável publicada. Veja [instalação](../INSTALL.md) e [notas da versão](../RELEASE-1.3.0.md).

Versões da publicação: cytv **0.4.0**, Home **1.4.2**, Home Helper **0.6.19**, Root **0.4.0**, Home Updater e Root Updater **0.3.0**, Android **0.3.0-preview** (código **11**), supervisor System Updater **1.1.0**, protocolo **1**.

Problema conhecido da 1.3.0: após o modo de espera, o controle Home do Root pode desligar e Home volta a abrir a LG. Ative-o novamente de forma explícita nos ajustes do Clean Your TV; se falhar, mantenha a LG Home e salve o diagnóstico. Veja a [issue #90](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/90) e os [testes atuais](../RELEASE-1.3.0-ACCEPTANCE.md).

Ligue a TV e conecte os dois dispositivos à mesma rede local confiável. Depois, o computador pode ficar desligado. A compatibilidade depende do modelo, firmware e controle remoto; Root ainda tem testes em hardware pendentes.

- **No-root:** ative LG Developer Mode e Key Server. Digite a frase de acesso exibida na TV e aceite nela o pedido separado de pareamento. Developer Mode deve continuar ativo: a expiração pode remover aplicativos instalados por esse método. Confira o cronômetro oficial mesmo com a renovação Beta ativada. O monitoramento do Helper depende da rede local.

O Helper No-root atualizado exige Node.js 0.12.2 ou posterior na TV. O instalador verifica esse requisito antes da instalação. Pacotes publicados anteriormente não recebem essa compatibilidade automaticamente; o acesso ao controle, a espera e a inicialização a frio precisam ser testados em cada modelo.

- **Root:** é necessário acesso SSH root já existente. O instalador não faz root. Não ative Developer Mode em uma TV que já tenha root. Mantenha o acesso root e os serviços de recuperação disponíveis.


## Configurar Developer Mode (No-root)

Developer Mode permite ao CYTV instalar apps em uma TV sem root.

1. Na TV, abra LG Apps, procure Developer Mode e instale o app.
2. Abra Developer Mode e entre com sua conta LG Developer. Se necessário, crie uma conta em webostv.developer.lge.com.
3. Ative Dev Mode Status. A TV reiniciará. Depois, abra Developer Mode novamente.
4. Ative Key Server e deixe Developer Mode aberto. Use o IP Address exibido como endereço da TV no CYTV.
5. Digite a Passphrase: os seis caracteres exibidos no Developer Mode da TV. Respeite maiúsculas e minúsculas.

Use o código da TV, não a senha da sua conta LG. Se o código não aparecer, ative Key Server.

O pareamento é uma etapa separada: quando a TV pedir, autorize o CYTV com o controle remoto.

Mantenha Developer Mode ativo: antes de o tempo acabar, abra o app e pressione EXTEND com a TV conectada à Internet. Se expirar, a LG pode remover esses apps.

Home é sua tela de apps. Home Helper faz o botão Home abrir essa tela.

Após instalar, pressione Home para testar. Se LG Home abrir, abra Home Helper na lista de apps da TV. Pressione Home brevemente três vezes em dois segundos para voltar ao LG Home. Para reiniciar o controle de Home, abra Home Helper, escolha Iniciar Helper e confirme. Sua tela Home escolhida será mantida.

No computador, o CYTV mostra a preparação passo a passo. Detalhes abre o registro da operação. As imagens de exemplo da LG podem ser ampliadas; use o código da sua TV.

[LG Developer Mode](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)

## Python opcional para Root

Root exige Python 3.9+ na TV. O instalador verifica os módulos e operações de verdade, incluindo `json`, `fcntl`, bloqueios, arquivos e subprocessos; o número da versão não basta. Se o interpretador existente for adequado, não há outro download de Python. Caso contrário, durante a configuração, o computador ou Android pode baixar CPython **3.13.17 para ARMv7 soft-float**, fixado por URL, tamanho e SHA-256, e transferi-lo pela conexão SSH já confiável. Os pacotes comuns dos instaladores não incluem esse arquivo; a TV não precisa de Internet nessa etapa.

O download opcional tem cerca de **26,3 MB**, a transferência SSH normalizada **51,5 MB** e os arquivos instalados **119,3 MB**; a preparação exige **320 MiB** livres na TV. A compatibilidade do carregador e das bibliotecas é verificada antes da ativação. O runtime ocupa versões privadas em `/var/lib/clean-your-tv-python/`, sem alterar Python do sistema, libc ou PATH global. Os demais requisitos continuam: root, serviços webOS adequados e Node.js **8+** para Root/System Updater; o Helper No-root precisa de Node.js **0.12.2+**.

Em um computador com Internet, prepare o cache verificado sem descobrir nem contatar uma TV:

```sh
./cytv --prepare-python-runtime --data-dir /caminho/cache-privado
```

Use o mesmo `--data-dir` na instalação. Para transportar o cache, crie uma pasta privada separada, sem suas chaves SSH e perfis habituais. `status`, `doctor`, `restore` e `uninstall` não baixam Python automaticamente. Preserve as versões usadas por Root, atualizadores e recuperação, mesmo depois de remover os aplicativos. Detalhes: [runtime opcional](../OPTIONAL-PYTHON.md).

## Instalação e idioma

- **Windows x64:** baixe `cytv-windows-x64-desktop.zip`, escolha **Extrair tudo** no Explorador de Arquivos e abra `cytv-desktop/cytv-desktop.exe`. Mantenha a pasta `_internal` ao lado. A assinatura de editor do Windows não está configurada. O console separado é `cytv-windows-x64.exe`; renomeie para `cytv.exe` e use `.\cytv.exe` no PowerShell para os comandos abaixo.
- **macOS 13+:** extraia `cytv-macos-arm64.zip` para Apple Silicon ou `cytv-macos-x64.zip` para Intel; mova `cytv.app` para Aplicativos e abra. Permita acesso à rede local. Se uma cópia confiável for bloqueada, use Privacidade e Segurança → Abrir Mesmo Assim; não desative o Gatekeeper. A compatibilidade com sistemas antigos não foi confirmada.
- **Linux x64:** no Ubuntu 22.04+, Debian 12+ ou Mint 21+, instale `cytv-linux-x64.deb` com o gerenciador gráfico de pacotes e abra Clean Your TV pelo menu. Pode ser necessário acesso à Internet para bibliotecas. Não há pacote Linux ARM. O executável independente `cytv-linux-x64` é a CLI; use o `.deb` para o app gráfico.

[Instalador Android](../../android/README.md): inclui os doze idiomas da interface. O controle no canto superior direito mostra o idioma atual; toque para escolher outro. A seleção fica salva no telefone.

No Android, a ação de manutenção escolhida continua visível durante a conexão e mostra seu próprio progresso. A interface usa a fonte do sistema do telefone, com rótulos e textos de ajuda maiores.

O assistente usa inicialmente o idioma do sistema e salva sua escolha explícita. Na TV, abra **Configurações → Idioma** e escolha um idioma ou a opção automática do sistema. As preferências da TV e do instalador são independentes. Veja os códigos no [índice de idiomas](../LANGUAGES.md).

Para a CLI baixada separadamente no macOS/Linux, na pasta extraída:

```sh
chmod +x cytv
./cytv --language pt-BR install
```

Escolha a TV ou informe o IP, selecione a edição e confira o resumo. Confirme uma nova identidade SSH apenas para sua TV em uma rede confiável; uma chave salva que mudou bloqueia o acesso. Root prepara a recuperação e ativa Home imediatamente, sem período de teste nem etapa de confirmação para manter. Teste setas, OK, Home, Voltar/Cancelar, volume, espera e inicialização a frio.

Se a remoção de Root for interrompida, escolha Remover novamente no app. Ele verifica o registro da TV e os pacotes antes de continuar; não repete uma remoção concluída. Se ainda estiver em andamento, aguarde um minuto. Se o resultado não puder ser verificado, reinicie a TV e verifique novamente; guarde o relatório para o suporte.

## Uso e recuperação

Setas selecionam; OK abre; segure OK para reorganizar. Um toque em Voltar mantém a navegação e a confirmação de saída do aplicativo. Home abre o lançador com o controle ativo. Nas novas compilações, segure Voltar por 1,2 segundos para abrir LG Home uma vez. O interruptor de controle do Home e suas configurações não mudam.

**Novas compilações: pressione Home três vezes em dois segundos**, soltando entre os toques. Isso restaura LG Home e interrompe o controle sem apagar preferências. No No-root Helper até a versão 0.6.13, segure Home por cerca de dois segundos. Segurar Home não é o gesto de emergência do Root.

No-root: Pressione Home brevemente três vezes em dois segundos para voltar ao LG Home. Para reiniciar o controle de Home, abra Home Helper, escolha Iniciar Helper e confirme. Sua tela Home escolhida será mantida. Root: ative **Alterar Home** nas configurações do Home para retomar. **Abrir LG Home** abre LG Home uma vez sem mudar o destino de Home. Para restaurar LG Home como destino permanente, desative **Alterar Home** ou execute `cytv restore`. Nunca execute os dois controladores juntos. Se a falha voltar, mantenha LG Home ativo.

```sh
./cytv --language pt-BR status
./cytv --language pt-BR doctor --report
./cytv --language pt-BR restore
./cytv --language pt-BR uninstall
```

Após uma interrupção, execute primeiro `status` e preserve os registros. `restore` restaura LG Home sem remover aplicativos; `uninstall` restaura antes de remover. Os dados de recuperação Root são mantidos de propósito: não os apague para forçar a reinstalação. Revise relatórios antes de compartilhar; não publique chaves nem pastas de perfis.

## Atualização e remoção

Após conectar, cytv mostra versão instalada → incluída e diferencia primeira instalação, reinstalação e retorno a uma versão anterior. Confira o resumo antes de confirmar; `--yes` mantém as verificações de compatibilidade. Guarde pacotes funcionais e cópias privadas das configurações. Ao atualizar pelo computador, pare o No-root Helper antes de substituir os pacotes; não desinstale primeiro. Não instale uma IPK isolada sobre Root ativo: use o procedimento adequado do cytv. Remover o aplicativo do computador não remove os aplicativos da TV.

A candidata acrescenta **Atualizar tudo** em Configurações → Atualizações de software. O System Updater independente verifica um conjunto assinado para a edição: Home, Helper e Home Updater para No-root em TV com root; Root Home, Root Updater e runtime de controle/recuperação para Root. Atualizar pela TV exige **root, Homebrew Channel**, Python adequado, Node.js 8+ e serviços webOS funcionais. Em TV sem root, use o computador.

Em uma instalação nova, use o instalador completo da candidata para preparar Home e o Updater de recuperação da edição. Essa versão de transição não está disponível no feed estável.

Se Root já estiver instalado e houver um Root Updater preservado, uma reinstalação genérica poderá ser recusada por segurança. Primeiro execute `status` e os diagnósticos, depois confira a transação e a recuperação no Updater existente. Resolva operações ativas ou incertas pelo fluxo de recuperação correspondente à instalação anterior; a transição de infraestrutura precisa ser avaliada conforme o estado real da TV. Não apague o diário nem contorne o bloqueio com `--yes`, uma IPK isolada ou OTA antigo. O OTA apenas do aplicativo não instala a nova infraestrutura. Siga o [verificação da TV existente](../UPDATES.md#one-time-computer-preparation).

Só depois de verificar uma configuração compatível com Home `systemUpdateProtocol = 1` e o Updater de recuperação adequado, habilite o supervisor pelo computador. No instalador, escolha habilitar as atualizações de todos os componentes da TV; para Root, com uma conexão SSH root salva:

```sh
./cytv --language pt-BR enable-system-updates --edition root --host TV_ADDRESS
```

Para No-root em TV com root, prepare Home/Helper/Home Updater pelo computador e siga o procedimento com alias SSH root em [Atualizações](../UPDATES.md#one-time-computer-preparation). O supervisor captura uma base verificada de recuperação dos componentes realmente instalados. O OTA antigo que troca apenas o aplicativo não instala o novo Python, supervisor ou infraestrutura dos atualizadores. Depois da preparação, use o fluxo comum; instaladores antigos conflitantes são recusados.

A instalação pede confirmação e depois verifica a inicialização automaticamente. Perfil e configurações são preservados; uma parada explícita ou de emergência do controle Home não é desfeita. Cima/Baixo percorre as notas, Esquerda/Direita escolhe as ações fixas e a atualização de estado mantém o foco do controle. Um ponto laranja indica nova versão, inclusive quando exige o computador. Abra Recuperação no Updater para consultar o estado e a versão anterior disponível. O retorno do sistema restaura todo o conjunto anterior e o perfil salvo; alterações posteriores nas configurações podem ser perdidas. A verificação automática de inicialização não apaga a recuperação, que permanece até a próxima transação.

Após uma interrupção, execute `status` e preserve o diário e os dados de recuperação. Um resultado incerto bloqueia reinstalação e retorno; ler a versão não comprova que o instalador terminou. Não apague diários, bloqueios ou versões do Python para forçar outra tentativa. `doctor --report` identifica cada requisito Root que falhou e registra códigos numéricos SSH sem credenciais ou saída bruta. Revise o relatório antes de compartilhar.

## Testes em hardware e limites

Root 0.2.0, Root Updater 0.2.0 e supervisor 1.0.0 foram verificados em OLED55C3RLA / firmware 43.21.71 / webOS 11.2.0 (`d344d92`, conteúdo idêntico a `4b66951`). Passaram controles, Home triplo e retomada, espera/retomada com Emby aberto por 70 segundos, menus de versões e aviso claro de feed indisponível. Inicialização a frio real, Helper 0.6.19 na TV, UK6540PTD e atualização/retorno completo assinado não foram testados. A publicação estável aceita essas evidências limitadas; outros modelos não estão validados.

No-root verifica a ABI do shell e aceita kernel de 64 bits somente com ambiente ARM32 confirmado. Nome de modelo ou `armv7l` não garante compatibilidade. As evidências anteriores continuam restritas ao hardware e aos pacotes testados.

No-root: Configurações Home → Modo de desenvolvedor reúne renovação Beta, verificação de sessão e diagnósticos. Confira sempre o cronômetro oficial. Home Helper mostra o estado e pede confirmação para retomar após uma parada.

Documentação técnica: [desktop](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [instalação manual](../MANUAL_INSTALL.md), [recuperação](../RECOVERY.md), [edições](../EDITIONS.md), [atualizações](../UPDATES.md).

Se Root mostrar `Denied methods call status` logo após preparar o supervisor, feche e reabra Home Root uma vez e verifique as atualizações novamente. Se persistir, guarde o diagnóstico e o estado de recuperação.

1.2.0 (#51): após a TV rejeitar um pacote, o relatório JSON preserva apenas a categoria da operação, códigos numéricos limitados, um estado de pacote permitido e um resultado booleano. Exclui o texto bruto do erro da TV, caminhos e IDs de aplicativos. Revise antes de compartilhar; não há nova tentativa automática e a falha de instalação no UN70006LA ainda não foi confirmada como corrigida.

1.2.0 (#59): se o estado do Helper não puder ser verificado, **Iniciar Helper** continua disponível com confirmação. Abrir o bloco não reinicia o Helper nem cancela uma parada de emergência. Os ajustes de Home exigem que o controle responda.

1.2.0 (#55): o Root valida a migração antes de instalar. Uma instalação interrompida antes do provisionamento pode ser removida sem um snapshot LS2 que nunca foi criado; um registro verificado é preservado para o arquivamento e a reinstalação normais do cytv. Snapshots ausentes em etapas posteriores ou evidências conflitantes ainda bloqueiam a limpeza. Exige o novo driver; a falha ao iniciar o serviço de recuperação no OLED Flex continua sem solução.

## Bloqueio de firmware LG no 1.2.0

Somente Root: Configurações do Home → Atualizações de firmware da LG altera a configuração existente do Homebrew Channel. Inclui atualizações de segurança do firmware; as do Clean Your TV são separadas. Ambas as alterações exigem reiniciar a TV de verdade; o modo de espera não basta. O botão mostra a configuração salva, não um bloqueio ativo verificado. Algumas TVs verificam antes do bloqueio; os avisos podem continuar e pode ser necessário bloquear no roteador. O Homebrew mantém a configuração após remover ou reverter o CYTV. Se indisponível ou não confirmado, verifique o Homebrew e atualize o status. Veja o alcance dos testes no registro de aceitação.

[LG firmware blocking](../LG-FIRMWARE-UPDATES.md) · [1.2.0](../RELEASE-1.2.0-ACCEPTANCE.md)

## Novidades da 1.3.0: recuperação guiada no computador

Novidades da 1.3.0. Após verificar o estado da TV, diagnosticar a conexão ou voltar ao LG Home, uma remoção No-root incompleta oferece **Recuperar e reinstalar** para a mesma TV e conexão. Confirme explicitamente a conclusão da remoção (padrão: Não) e revise as versões incluídas antes de instalar. **Configurar minha TV** também oferece esse caminho. Voltar ao LG Home sozinho não conclui a remoção. Em caso de falha, use **Salvar relatório de diagnóstico…** para salvar o relatório daquela tentativa e anexá-lo ao problema; não é necessário terminal. Se o relatório não puder ser criado, informe o erro visível. Mantenha os dados de recuperação; operações com falha ou resultado incerto não são repetidas automaticamente. Isso ainda não confirma a correção da falha no G5 com firmware 43.21.71 (#65).

## Novidades da 1.3.0 — #12

As Ferramentas do Android mantêm a TV, a edição e a porta SSH ao retornar à tela inicial; No-root normalmente usa 9922. Se os ajustes não conseguirem verificar o controle de Home, mostram um estado desconhecido e ocultam Alterar Home até receber uma resposta válida. Isso não significa que o Helper parou e não o reinicia. Essas mudanças não estão nos pacotes publicados da v1.2.0.

Diagnóstico Root da 1.3.0 (#55): após uma falha na instalação, salve o relatório dessa tentativa. Ele pode incluir categorias de erros de inicialização do serviço de recuperação; preserve os dados de recuperação e o driver instalado. A correção no OLED Flex ainda não foi confirmada.

## Candidato não publicado: instalar Root pelo Homebrew

Este código adiciona o aplicativo separado **CYTV Installer**, apenas para **Root**.
Ele ainda não foi publicado no catálogo Homebrew. cytv mantém No-root e Root no
Windows, macOS, Linux e Android; os links existentes continuam sendo do cytv.

Exige root já disponível, Homebrew Channel com execução como root, Node.js **8+**
e Python **3.9+** funcional. Há Python privado fixado e offline para ARMv7/`armv8l`
compatível com ambiente de 32 bits. Abrir e consultar o estado não altera nada:
prepare explicitamente Python se faltar, verifique novamente e revise a instalação.
São necessários **320 MiB livres após instalar Installer**; o espaço adicional de
preparação de pacotes no TV ainda não foi medido. Não há confirmação de compatibilidade
com novos modelos ou firmware.

São instalados Root Home e Root Updater; preparar System Updater é uma opção
explícita. Ative Change Home separadamente depois da verificação. Parada de emergência
e preferência desativada continuam preservadas. Uma instalação atual verificada
compartilha perfil e recuperação entre cytv e TV sem reinstalar nem redefinir.
Infraestrutura antiga desconhecida exige diagnóstico; importar preferências
empacotadas serve para uma instalação nova, não para navegador nem infraestrutura.

Após interrupção, consulte primeiro o estado. Continuar exige a cópia e reserva
originais com estado final comprovado. Outras etapas exigem estado, restauração
ou diagnóstico; a CLI do código pode continuar explicitamente outras etapas
reconhecidas. Finish Root setup do cytv não reinicia um processo incompleto. Não
apague diários nem repita às cegas. Homebrew atualiza somente Installer; o produto
usa os Updaters existentes e conjuntos completos assinados. Excluir Installer
mantém o produto. A remoção completa restaura LG Home e limpa os links de início
próprios, preservando recuperação independente, arquivos e Python necessário.
Todos os testes físicos deste caminho estão pendentes; os resultados históricos
Root 0.2.0 no C3 não o validam.

A inicialização usa arquivos privados vinculados aos comprovantes de propriedade e verifica a identidade do pacote como dados. Scripts de inicialização do pacote nunca são executados. Pacotes ausentes ou inseguros impedem a retomada automática; a recuperação independente ainda pode restaurar LG Home. A inspeção pode copiar temporariamente arquivos verificados para uma área privada sem alterar Home nem o produto.

[Instalação e recuperação (inglês)](../INSTALL.md#candidate-on-tv-root-installation) ·
[Testes físicos pendentes (inglês)](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)


Para este candidato do código-fonte, uma instalação Root existente precisa de recuperação verificada e nova configuração para receber o ambiente privado corrigido. Atualizar apenas o Installer não o substitui. Preserve os registros de recuperação e ative Home somente pela configuração ou pelos ajustes normais.

Somente no próximo candidato: No-root Configurações → Modo de desenvolvedor → Mostrar diagnóstico inclui categorias seguras de falhas de armazenamento e RPC do Home e a versão real do serviço. A consulta não ativa a renovação nem inicia o Helper. Uma falha na consulta não prova que o Helper parou. A correção no C5 não foi confirmada; [detalhes (inglês)](../SETTINGS-DIAGNOSTICS.md).

O relatório recebe o foco do controle. Cima/Baixo rola; Esquerda/Direita ou OK volta às ações próximas e Voltar às configurações do Home.
