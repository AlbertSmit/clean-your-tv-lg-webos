# Clean Your TV — guía de uso

1.4.0: el responsable aceptó las pruebas corregidas del C3 de encendido, Home, foco, estado desactivado y reversión manual a 1.3.0; #90 se cerró a su petición. Otros televisores, audio eARC y Android físico siguen sin verificar. No se repitieron todos los botones básicos del candidato anterior. [1.4.0 acceptance (English)](../RELEASE-1.4.0-ACCEPTANCE.md). Earlier pending statements below are historical.


No-root y Root son opciones equivalentes para distintas configuraciones del televisor. Elige No-root para LG Developer Mode o Root si ya tienes acceso root por SSH. La compatibilidad y las pruebas realizadas son específicas de cada edición.

## Requisitos

Esta guía describe **[v1.3.0 estable](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0)**. Los enlaces `releases/latest/download` entregan la versión estable publicada. Consulta [instalación](../INSTALL.md) y [notas de la versión](../RELEASE-1.3.0.md).

La versión incluye cytv **0.4.0**, Home **1.4.2**, Home Helper **0.6.19**, Root Edition **0.4.0**, Home Updater y Root Updater **0.3.0**, Android **0.3.0-preview** (código de versión **11**) y el supervisor System Updater **1.1.0** (protocolo **1**). Estos son los componentes de v1.3.0.

El candidato 1.4.0 aún no publicado incluye Android 0.4.0 (código 13) sin preview tras las pruebas de emulador aceptadas por el mantenedor. Probado: Android 15 ARM64 / WebView 124. Los teléfonos físicos y la recuperación durante una instalación real en el TV no están verificados; Android 7 / WebView 108 es un requisito mínimo, no un teléfono probado. Actualice sin desinstalar ni borrar datos. Las descargas publicadas siguen en 0.3.0-preview. Comunique teléfono, Android/WebView, TV/firmware, edición y paso fallido, sin credenciales.

Problema conocido de 1.3.0: después del modo de espera, el control Home de Root puede desactivarse y Home vuelve a abrir LG. Actívalo de nuevo explícitamente en los ajustes de Clean Your TV; si falla, conserva LG Home y guarda el diagnóstico. Consulta [issue #90](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/90) y las [pruebas actuales](../RELEASE-1.3.0-ACCEPTANCE.md).

Root 0.2.0, Root Updater 0.2.0 y supervisor 1.0.0 se comprobaron en OLED55C3RLA / firmware 43.21.71 / webOS 11.2.0 (`d344d92`, contenido idéntico a `4b66951`). Pasaron los controles, triple Home y reanudación, reposo/reactivación con Emby abierto durante 70 segundos, menús de versiones y aviso claro de canal no disponible. No se probaron el arranque en frío real, Helper 0.6.19 en TV, UK6540PTD ni actualización/restauración completa del sistema firmada. La publicación estable acepta estas pruebas limitadas; otros modelos no están validados.

Enciende el televisor y conecta ambos equipos a la misma red local de confianza. Después, el ordenador puede estar apagado. La compatibilidad depende del modelo, firmware y mando; Root tiene pruebas físicas pendientes.

- **No-root:** activa LG Developer Mode y Key Server. Introduce la frase de acceso que muestra el televisor y acepta en él la solicitud de emparejamiento independiente. Developer Mode debe permanecer activo: su caducidad puede eliminar aplicaciones instaladas por este método. Vigila el temporizador oficial incluso con la renovación Beta activada. La supervisión de Helper necesita la red local.

El Helper No-root actualizado requiere Node.js 0.12.2 o posterior en el TV. El instalador comprueba este requisito antes de instalar. Los paquetes publicados anteriormente no adquieren esta compatibilidad automáticamente; el acceso al mando, la espera y el arranque en frío requieren pruebas en cada modelo.

- **Root:** necesitas acceso SSH root previo. El instalador no obtiene root. No actives Developer Mode sobre una instalación ya rooteada. Conserva el acceso root y los servicios de recuperación.


## Configurar Developer Mode (No-root)

Developer Mode permite a CYTV instalar apps en un TV sin root.

1. En el TV, abre LG Apps, busca Developer Mode e instálalo.
2. Abre Developer Mode e inicia sesión con tu cuenta LG Developer. Si necesitas una, créala en webostv.developer.lge.com.
3. Activa Dev Mode Status. El TV se reiniciará. Después, abre Developer Mode de nuevo.
4. Activa Key Server y deja Developer Mode abierto. Introduce su IP Address como dirección del TV en CYTV.
5. Introduce la Passphrase: los seis caracteres que muestra Developer Mode en el TV. Respeta mayúsculas y minúsculas.

Usa el código del TV, no la contraseña de tu cuenta LG. Si no aparece el código, activa Key Server.

El emparejamiento es un paso aparte: cuando el TV lo pida, acepta CYTV con el mando.

Mantén Developer Mode activo: antes de que termine el tiempo, ábrelo y pulsa EXTEND con el TV conectado a Internet. Si caduca, LG puede eliminar estas apps.

Home es tu pantalla de apps. Home Helper hace que el botón Home la abra.

Tras instalar, pulsa Home para probarlo. Si se abre LG Home, abre Home Helper desde las apps del TV. Pulsa Home brevemente tres veces en dos segundos para volver a LG Home. Para reiniciar el control de Home, abre Home Helper, elige Iniciar Helper y confirma. Se conserva tu pantalla Home elegida.

CYTV en el ordenador muestra la preparación paso a paso. Detalles abre el registro de la operación. Puedes ampliar las imágenes de LG; usa el código de tu propio TV.

[LG Developer Mode](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)

## Python opcional para Root en v1.1.0

Root necesita Python **3.9+** funcional en el televisor. El instalador comprueba los módulos necesarios (entre ellos `json` y `fcntl`), los bloqueos, las operaciones con archivos y los subprocesos; el número de versión no basta. Si ya hay un intérprete adecuado, no se descarga otro. En caso contrario, la configuración descarga **CPython 3.13.17 para ARMv7 soft-float** verificado en el ordenador o dispositivo Android y lo transfiere por SSH de confianza; el televisor no necesita Internet. El archivo opcional no viene incluido en los instaladores habituales: unos **26.3 MB** de descarga, **51.5 MB** de transferencia SSH normalizada y **119.3 MB** instalados; se requieren **320 MiB** libres para la preparación inicial. Este entorno privado no sustituye Python del sistema, libc ni el PATH global.

Siguen siendo necesarios un cargador y bibliotecas compatibles. Se mantienen los requisitos de root SSH, Node.js **8+**, `luna-send` y los directorios de aplicaciones y servicios de webOS; No-root Helper necesita Node.js **0.12.2+**. El LG UK6540PTD / firmware 05.50.70 / ARM32 del issue #37 (Python 2.7.12 sin Python 3) **no ha superado la validación física** con este entorno. Las pruebas QEMU no validan el televisor, el arranque en frío, el mando ni la restauración. Los resultados físicos anteriores se limitan a los modelos, firmware y archivos documentados.

Para preparar una caché verificada en un ordenador con Internet **sin contactar con un televisor**:

```sh
./cytv --language es --prepare-python-runtime
```

Usa el mismo directorio privado de datos para instalar. Para trasladar la caché, prepara un directorio nuevo dedicado con `--data-dir /path/to/private-data` y usa esa opción en ambos comandos. No copies las claves SSH y perfiles habituales a una caché compartida. El estado, diagnóstico, restauración y eliminación no descargan Python automáticamente. Conserva las versiones del entorno que usen los actualizadores instalados o la recuperación. Consulta los [detalles de Python](../OPTIONAL-PYTHON.md).

## Instalación e idioma

- **Windows x64:** descarga `cytv-windows-x64-desktop.zip`, elige **Extraer todo** en el Explorador y abre `cytv-desktop/cytv-desktop.exe`. Conserva la carpeta `_internal` a su lado. No se ha configurado la firma de editor de Windows. La consola separada es `cytv-windows-x64.exe`; renómbrala a `cytv.exe` y usa `.\cytv.exe` en PowerShell para los comandos siguientes.
- **macOS 13+:** extrae `cytv-macos-arm64.zip` para Apple Silicon o `cytv-macos-x64.zip` para Intel, mueve `cytv.app` a Aplicaciones y ábrela. Permite el acceso a la red local. Si se bloquea una descarga de confianza, usa Privacidad y seguridad → Abrir igualmente; no desactives Gatekeeper. La aceptación en sistemas antiguos no está confirmada.
- **Linux x64:** en Ubuntu 22.04+, Debian 12+ o Mint 21+, instala `cytv-linux-x64.deb` con el gestor gráfico de paquetes y abre Clean Your TV desde el menú de aplicaciones. Las bibliotecas pueden requerir Internet. No hay paquete Linux ARM. El ejecutable independiente `cytv-linux-x64` es la CLI; usa el `.deb` para la app gráfica.

[Instalador Android](../../android/README.md): incluye los doce idiomas de la interfaz. El control superior derecho muestra el idioma actual; tócalo para elegir otro. La selección se guarda en el teléfono.

En Android, la acción de mantenimiento elegida sigue visible durante la conexión y muestra su propio progreso. Se usa la fuente del sistema del teléfono con etiquetas y ayudas más grandes.

El asistente de escritorio usa inicialmente el idioma del sistema y guarda una selección explícita. En el televisor, abre **Ajustes → Idioma** y elige un idioma o la opción automática del sistema. Las preferencias del instalador y del televisor son independientes. Consulta los códigos en el [índice de idiomas](../LANGUAGES.md).

Para la CLI descargada por separado en macOS/Linux, desde la carpeta extraída:

```sh
chmod +x cytv
./cytv --language es install
```

Selecciona el televisor o introduce su IP, elige la edición y revisa el resumen. Confirma una nueva identidad SSH solo para tu televisor en una red de confianza; una clave guardada que haya cambiado bloquea el acceso. Root prepara la recuperación y activa Home inmediatamente, sin prueba temporal ni paso de conservación. Comprueba flechas, OK, Home, Atrás/Cancelar, volumen, suspensión y arranque en frío.

Si se interrumpe la eliminación de Root, elige Eliminar otra vez en la app. Comprobará el registro de la TV y los paquetes antes de continuar; no repetirá una eliminación completada. Si sigue en curso, espera un minuto. Si no se puede verificar el resultado, reinicia la TV y comprueba otra vez; conserva el informe para soporte.

## Uso y recuperación

Las flechas seleccionan y OK abre; mantén OK para reordenar. Una pulsación breve de Atrás conserva la navegación y confirmación de salida de cada aplicación. Home abre el lanzador mientras el control está activo. En las nuevas compilaciones, mantén Atrás durante 1,2 segundos para abrir LG Home una vez. El interruptor de control de Home y tus ajustes no cambian.

**Compilaciones nuevas: pulsa Home tres veces en dos segundos**, soltando entre pulsaciones. Se recupera LG Home y se detiene el control sin borrar preferencias. En No-root Helper hasta 0.6.13 inclusive, mantén Home unos dos segundos. Mantener Home no es el gesto de emergencia de Root.

No-root: Pulsa Home brevemente tres veces en dos segundos para volver a LG Home. Para reiniciar el control de Home, abre Home Helper, elige Iniciar Helper y confirma. Se conserva tu pantalla Home elegida. Root: activa **Cambiar Home** en los ajustes de Home para reanudar. **Abrir LG Home** lo abre una vez sin cambiar el destino de Home. Para recuperar LG Home como destino permanente, desactiva **Cambiar Home** o ejecuta `cytv restore`. No ejecutes ambos controladores a la vez. Si el fallo se repite, deja LG Home activo.

```sh
./cytv --language es status
./cytv --language es doctor --report
./cytv --language es restore
./cytv --language es uninstall
```

Tras una interrupción, ejecuta primero `status` y conserva los registros. `restore` recupera LG Home sin quitar aplicaciones; `uninstall` lo restaura antes de eliminarlas. Los datos de recuperación Root se conservan deliberadamente: no los borres para forzar otra instalación. Revisa los informes antes de compartirlos; no publiques claves ni carpetas de perfiles.

## Actualizaciones y eliminación

Guarda paquetes funcionales y copias privadas de ajustes. Para sustituir paquetes No-root desde el ordenador, detén Helper primero y actualiza sin desinstalar, ya que podrías perder ajustes. Eliminar la aplicación del ordenador no elimina las aplicaciones del televisor. No sustituyas un entorno Root activo con una IPK suelta; usa el proceso explícito de recuperación o reinstalación de cytv.

En v1.1.0, **Actualizar todo** en Ajustes de Home → Actualizaciones de software usa un conjunto firmado: Home, Helper y Home Updater para No-root en un televisor con root; Root Home, Root Updater y el entorno de control de Home y recuperación para Root. Requiere root, Homebrew Channel, servicios de instalación webOS funcionales, Python 3.9+ y Node.js 8+. Un televisor sin root sigue usando el instalador del ordenador.

Para una instalación nueva, usa el instalador completo estable para instalar la versión de transición de Home y el actualizador de recuperación de la edición correspondiente. **Una instalación Root existente con Root Updater conservado puede bloquear deliberadamente una reinstalación genérica.** Revisa primero `status`, Recuperación y la transacción existente mediante el proceso de recuperación correspondiente a la instalación antigua; consulta la [comprobación del televisor ya instalado](../UPDATES.md#one-time-computer-preparation). No borres registros ni omitas esta comprobación. Una actualización OTA antigua de solo Home no instala la nueva infraestructura.

Activa las **actualizaciones de todos los componentes del TV** en el instalador de escritorio solo cuando los componentes instalados y el estado de recuperación estén preparados. Para una conexión SSH root guardada y la edición Root:

```sh
./cytv --language es enable-system-updates --edition root --host TV_ADDRESS
```

Esta acción independiente instala el supervisor fijo y guarda el conjunto instalado como base para restaurarlo. Exige `systemUpdateProtocol = 1` en los metadatos de Home instalado; no reinstala Home ni cambia su destino. La edición No-root habitual en un televisor con root necesita SSH root y los componentes correspondientes instalados desde el ordenador; consulta la [preparación inicial](../UPDATES.md#one-time-computer-preparation). Una actualización OTA antigua de solo Home **no instala** la nueva infraestructura del supervisor, Python o los actualizadores. Tras instalar el supervisor se bloquean los instaladores antiguos incompatibles; no sustituyas paquetes al margen de él.

Las actualizaciones del sistema verifican y guardan en caché el conjunto candidato y el anterior, conservan ajustes y perfiles y continúan aunque se cierre Home o un actualizador. La recuperación restaura el conjunto anterior completo y su perfil. Quedan pendientes nuevas pruebas físicas, incluida la liberación de entradas de Helper 0.6.19, el arranque en frío, la actualización completa y la restauración; las pruebas anteriores en C3 solo cubren sus paquetes documentados de Home. Consulta los [detalles de actualización y recuperación](../UPDATES.md).

Documentación técnica en inglés: [escritorio](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [instalación manual](../MANUAL_INSTALL.md), [recuperación](../RECOVERY.md), [ediciones](../EDITIONS.md).

Tras conectar, cytv lee las versiones del televisor y muestra la versión actual → incluida para Home y Home Helper (No-root), o Root y Root Updater. Revise y confirme antes de instalar. Se indican las instalaciones nuevas, reinstalaciones y versiones anteriores; `--yes` omite la confirmación, pero muestra las versiones.

Actualizaciones de software muestra detalles solo de la versión instalada o una más reciente. Abre Recuperación para ver la versión guardada para restaurar o por qué no está disponible; Atrás vuelve a las actualizaciones.

No-root comprueba la ABI de la consola del TV y acepta un núcleo de 64 bits con entorno ARM32 verificado. Si falla la comprobación, adjunta el JSON de diagnóstico generado; no compartas claves ni frases de contraseña.

Las actualizaciones de Home piden confirmación antes de instalar; después el inicio se verifica automáticamente. La actualización del estado conserva el botón seleccionado con el mando.

Ambas ediciones comprueban el arranque automáticamente; no hace falta confirmar manualmente que funciona. La restauración antigua de solo Home recupera el paquete anterior de Home y su perfil; System Updater recupera el conjunto anterior completo. La recuperación sigue disponible tras la confirmación, sin límite de tiempo, hasta la siguiente actualización. Los ajustes modificados después pueden perderse; la restauración pide confirmación. Actualizar y restaurar No-root en el TV sigue requiriendo root y Homebrew Channel. Tras una interrupción, ejecuta `status` y revisa Recuperación. Un resultado de instalación incierto bloquea la reinstalación y la restauración: conserva informes, registros y versiones del entorno, sin borrar el estado para forzar otro intento. Reanuda una operación cytv interrumpida solo mediante su proceso de recuperación verificado.

La pantalla de actualización separa versiones, estado y novedades legibles. Arriba/Abajo desplaza las notas; Izquierda/Derecha elige las acciones fijas de abajo. Tras las comprobaciones automáticas de inicio, Root restaura el control de Home si estaba activado; No-root conserva el estado del Helper independiente. Si estaba desactivado o se desactiva de forma explícita o de emergencia, sigue desactivado.

Al abrir los ajustes de Home se buscan actualizaciones en segundo plano. Un punto naranja en Actualizaciones de software indica una versión más reciente, incluso si requiere instalación desde el ordenador. Puedes seguir usando los ajustes durante la búsqueda.

No-root: abre Ajustes de Home → Modo de desarrollador para la renovación automática, la comprobación de sesión y el diagnóstico. La pantalla principal mantiene visibles el estado resumido y los errores de renovación. Atrás vuelve a los ajustes de Home. Ambas ediciones agrupan Idioma, Actualizaciones de software y Ajustes del TV en la misma fila; la flecha abre cada opción.

Al abrir Home Helper se muestran su función y estado. Iniciar un Helper detenido requiere confirmación. Home Updater y Root Updater explican la recuperación; las actualizaciones normales están en los ajustes de Home. La restauración solo se ofrece si hay una versión guardada y requiere confirmación antes de reemplazar Home y sus ajustes.

Si Root muestra `Denied methods call status` justo después de preparar el supervisor, cierra y abre Home Root una vez y vuelve a comprobar las actualizaciones. Si persiste, conserva el diagnóstico y los datos de recuperación.

[1.1.0 hardware acceptance](../RELEASE-1.1.0-ACCEPTANCE.md)

1.2.0 (#51): tras un rechazo de paquete por la TV, el informe JSON conserva solo la categoría de operación, códigos numéricos limitados, un estado de paquete permitido y un resultado booleano. Excluye el texto de error original, rutas e identificadores de aplicaciones. Revisa el informe antes de compartirlo; no hay reintento automático y no se ha confirmado que el fallo de instalación en UN70006LA esté resuelto.

1.2.0 (#59): si no se puede comprobar el estado de Helper, **Iniciar Helper** sigue disponible con confirmación. Abrir el icono no reinicia Helper ni desactiva una parada de emergencia. Los ajustes de Home requieren que responda el control.

1.2.0 (#55): Root valida la migración antes de instalar. Una instalación interrumpida antes del aprovisionamiento puede eliminarse sin una instantánea LS2 que nunca se creó; conserva un comprobante para el archivado y la reinstalación normales de cytv. La ausencia posterior de instantáneas o los datos contradictorios siguen bloqueando la limpieza. Requiere el nuevo controlador; el fallo de inicio del servicio de recuperación en OLED Flex sigue sin resolverse.

## Bloqueo de firmware LG en 1.2.0

Solo Root: Ajustes de Home → Actualizaciones de firmware de LG cambia el ajuste existente de Homebrew Channel. Incluye actualizaciones de seguridad del firmware; Clean Your TV se actualiza por separado. Ambos cambios requieren reiniciar realmente el TV; el modo de espera no basta. El interruptor muestra el ajuste guardado, no un bloqueo activo verificado. Algunos TV buscan actualizaciones antes del bloqueo; los avisos pueden persistir y puede ser necesario bloquear en el router. Homebrew conserva el ajuste al eliminar CYTV o volver a una versión anterior. Si no está disponible o confirmado, revisa Homebrew y actualiza el estado. Consulta el alcance de las pruebas en el registro de aceptación.

[LG firmware blocking](../LG-FIRMWARE-UPDATES.md) · [1.2.0](../RELEASE-1.2.0-ACCEPTANCE.md)

## Solo en la versión candidata: aspecto de Home opcional — No-root

Este código candidato añade **Ajustes → Pantalla de inicio → tvOS**. Elige **Actual** para volver al diseño actual y sus cinco temas de color. **Reducir efectos** limita los efectos visuales. Esta función no está incluida en la versión estable publicada que se describe arriba.

El aspecto tvOS muestra a pantalla completa una fotografía proporcionada por el usuario. El dock usa una copia local desenfocada previamente y la cuadrícula una miniatura; no hay recomendaciones de streaming ni filtros de desenfoque en vivo. Desplázate con Abajo o con la rueda del ratón. Arriba a la derecha hay un reloj compacto y un botón de Ajustes con forma de avatar. Haz clic en él o pulsa Arriba desde la primera fila de aplicaciones para mostrar Entradas, red y Ajustes. Atrás o Abajo vuelve a la cuadrícula.

El aspecto y los efectos se guardan solo en este televisor. Se conservan tras reinicios normales, pero no se incluyen en las copias del perfil y pueden perderse al reinstalar o transferir el perfil. Estos controles nuevos son solo para No-root. No se reproducen exactamente las fuentes, imágenes, movimientos ni efectos de Apple TV; el rendimiento en LG 50UP77006LB no se ha verificado.

En **Ajustes de Home → Widgets**, introduce la URL de Home Assistant y un token de acceso de larga duración. Deja vacía la entidad opcional del reproductor para detectar música en toda la casa, o indica una entidad para limitar la detección. Ahora suena aparece solo si HA confirma música en reproducción con un título; se oculta al pausar, detener o perder los datos. El tiempo conserva los marcadores cuando faltan datos. [Configurar widgets](../WIDGETS.md).

El interruptor **Widgets** de la cabecera muestra u oculta todos los widgets y desconecta las actualizaciones en vivo de HA cuando está apagado. Haz clic en él o, desde el dock, pulsa **Arriba → Derecha → OK** (Ajustes → Widgets); el foco vuelve al dock. La elección se conserva al reiniciar y no cambia los ajustes individuales. La tarjeta de música es compacta, de formato 2:1 y sin controles de reproducción. Usa la URL base del servidor del panel de HA, sin `/config/devices/...` ni rutas del panel, y crea el token en **Perfil → Seguridad**. Un HomePod registrado por sí solo no confirma los metadatos musicales necesarios.

HA envía actualizaciones en vivo por WebSocket tras cargar el estado inicial; no hay consultas REST periódicas. La conexión se cierra al ocultar el documento del TV o elegir el aspecto Actual. Los fallos temporales se reintentan con esperas de 1 a 30 segundos; un token inválido requiere corregir la configuración o reiniciar la conexión. El tiempo empieza desactivado en instalaciones nuevas; se respeta una activación guardada explícitamente. La tarjeta musical muestra la etiqueta Ahora suena, título y artista, sin álbum.

## Novedades de 1.3.0: recuperación guiada de escritorio

Novedades de 1.3.0. Después de comprobar el estado, diagnosticar la conexión o volver a LG Home, una desinstalación No-root incompleta ofrece **Recuperar y reinstalar** para el mismo TV y conexión. Confirma expresamente terminar la desinstalación (opción predeterminada: No) y revisa las versiones incluidas antes de instalar. **Configurar mi TV** también ofrece este recorrido. Volver a LG Home por sí solo no termina la desinstalación. Si falla, usa **Guardar informe de diagnóstico…** para guardar el informe de ese intento fallido y adjúntalo a tu incidencia; no necesitas terminal. Si no se pudo crear, incluye el error visible. Conserva los datos de recuperación; las operaciones fallidas o de resultado incierto no se repiten automáticamente. Esto aún no confirma una solución para el G5 con firmware 43.21.71 (#65).

## Novedades de 1.3.0 — #12

Herramientas de Android conserva el televisor, la edición y el puerto SSH al volver a la pantalla inicial; No-root usa normalmente 9922. Si los ajustes no pueden comprobar el control de Home, muestran un estado desconocido y ocultan Cambiar Home hasta recibir una respuesta válida. Esto no significa que Helper se haya detenido ni lo reinicia. Estos cambios no están en los paquetes publicados de v1.2.0.

Diagnóstico Root de 1.3.0 (#55): tras fallar la instalación, guarde el informe de ese intento. Puede incluir categorías de errores de inicio del servicio de recuperación; conserve los datos de recuperación y el controlador instalado. La solución en OLED Flex aún no está confirmada.

## Candidato sin publicar: instalar Root mediante Homebrew

Este código añade la aplicación independiente **CYTV Installer**, solo para
**Root**. Todavía no está publicada en el catálogo Homebrew. cytv conserva No-root
y Root en Windows, macOS, Linux y Android; los enlaces existentes siguen siendo de cytv.

Requiere root previo, Homebrew Channel con ejecución como root, Node.js **8+** y
Python **3.9+** funcional. Incluye Python privado fijado sin conexión para ARMv7/`armv8l`
compatible con entorno de 32 bits. Abrir o consultar el estado no instala nada:
prepare Python explícitamente si falta, vuelva a comprobar y revise la instalación.
Se necesitan **320 MiB libres después de instalar Installer**; aún no se ha medido
el espacio adicional de preparación de paquetes en un TV. No se confirma compatibilidad
con modelos o firmware nuevos.

Instala Root Home y Root Updater; preparar System Updater es opcional y explícito.
Active Change Home por separado después de verificar. No se borra la parada de
emergencia ni una preferencia desactivada. Una instalación actual verificada comparte
perfil y recuperación entre cytv y TV sin reinstalar ni restablecer. La infraestructura
antigua desconocida requiere diagnóstico; importar preferencias empaquetadas sirve
solo para una instalación nueva, no para datos del navegador ni infraestructura.

Tras una interrupción consulte primero el estado. Continuar exige la instantánea y
reserva originales y un estado final probado. Otros pasos requieren estado,
restauración o diagnóstico; la CLI del código puede continuar explícitamente otras
etapas reconocidas. Finish Root setup de cytv no reinicia un proceso incompleto.
No borre diarios ni repita a ciegas. Homebrew actualiza solo Installer; el producto
usa los actualizadores existentes y conjuntos completos firmados. Borrar Installer
conserva el producto. La eliminación completa restaura LG Home y limpia los enlaces
de inicio propios, conservando recuperación independiente, archivos y Python necesario.
Todas las pruebas físicas de esta vía están pendientes; las pruebas históricas
Root 0.2.0 del C3 no la validan.

El inicio usa archivos privados respaldados por comprobantes de propiedad y comprueba la identidad del paquete como datos. No ejecuta scripts de inicio del paquete. Si falta un paquete o no es seguro, se detiene el reinicio automático; la recuperación independiente aún puede restaurar LG Home. La inspección puede copiar temporalmente archivos verificados a un área privada sin cambiar Home ni el producto.

[Instalación y recuperación (inglés)](../INSTALL.md#candidate-on-tv-root-installation) ·
[Pruebas físicas pendientes (inglés)](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)


Para este candidato de código fuente, una instalación Root existente necesita recuperación verificada y una nueva configuración para recibir el entorno privado corregido. Actualizar solo Installer no lo sustituye. Conserve los registros de recuperación y active Home únicamente desde la configuración habitual.

Solo en el próximo candidato: No-root Ajustes → Modo de desarrollador → Mostrar diagnóstico incluye categorías seguras de errores de almacenamiento y RPC de Home, y la versión real del servicio. Consultarlo no activa la renovación ni inicia Helper. Un fallo de consulta no demuestra que Helper esté detenido. La corrección en C5 no está confirmada; [detalles (inglés)](../SETTINGS-DIAGNOSTICS.md).

El informe recibe el foco del mando. Arriba/Abajo desplaza; Izquierda/Derecha u OK vuelve a las acciones cercanas y Atrás a los ajustes de Home.

**Aún no publicado, #82:** si falta el ajuste Home, la instalación Root iniciada explícitamente puede establecer LG Home y verificar su lectura antes de completar la preparación de recuperación. Status/doctor no escribe nada. Una escritura de resultado incierto no se repite; conserva los datos de recuperación. El ajuste explícito de LG Home permanece tras la desinstalación. Faltan pruebas en esta versión del firmware.

## Candidato sin publicar: recuperación de sonido HDMI (Root)

Ajustes de Home → Sonido por HDMI ofrece reconexión eARC y recuperación de salida
HDMI confirmada. Se omiten ARC-only, combinados/WOW Orchestra y modos desconocidos.
La recuperación al encender/salir del reposo es experimental, desactivada por defecto;
requiere suscripción de energía compatible y puede interrumpir audio correcto.
Atrás cierra durante la limpieza. Tras interrupción, comprueba el estado; restaura
el ajuste solo si quieres eARC activado. Restaurar Home/parada de emergencia desactiva
la automatización hasta activación explícita. Runtimes privados antiguos necesitan
nueva configuración verificada. Compatibilidad y menor demora sin confirmar.

[Device acceptance (English)](../development/ROOT-AUDIO-RECOVERY.md)

Sin publicar: la comprobación de Python privado distingue errores de ABI, seguridad de directorios y espacio. La instalación inicial necesita 320 MiB libres en /var/lib. WAM Session Storage puede explicar la falta de espacio; borrarlo puede perder el estado de sesiones. Consulta la [recuperación](../RECOVERY.md#private-python-and-low-var-space).

En el candidato 1.4.0 aún no publicado, una instalación No-root interrumpida también ofrece **Recuperar y reinstalar** después de **Ver estado del televisor**. Confirma la eliminación solo si quieres quitar las apps de Clean Your TV y luego revisa las versiones antes de reinstalar. Si falla la recuperación, guarda su informe de diagnóstico y detente. Esto aún no identifica ni soluciona el rechazo original del paquete por el televisor (#21).


**Sin publicar — WAM:** `cytv clean-wam-cache --edition root`. Solo se solicitan cache y codecache. Se excluyen Session Storage, cookies, Local Storage, Service Worker y bases de datos. Cierra las apps del TV. La caché se descargará o creará de nuevo; el próximo inicio puede ser más lento. [WAM](../WAM-CLEANUP.md).

Puedes cancelar y liberar espacio tú mismo. Consulta la guía y revisa /var/lib; borrar apps puede liberar otra partición. **Session Storage (SSH):** Cierra primero las apps del TV. Se elimina el estado de sesión y puedes perder la sesión o trabajo sin guardar. [WAM](../WAM-CLEANUP.md#free-space-yourself-instead).

Corrección de arranque en frío de Root aún no publicada: con el control de Home activado y la pantalla de inicio de LG configurada en Home, un inicio protegido puede abrir Clean una vez si todavía aparece TV en directo o LG Home. Se conserva la aplicación visible en la última comprobación; no se reintenta. La desactivación explícita y tres pulsaciones de Home permanecen desactivadas. Se requiere instalar o actualizar de forma verificada el entorno privado; actualizar solo la aplicación no basta. La validación en el televisor sigue pendiente.

[Cold-start investigation and acceptance (English)](../development/ROOT-COLD-BOOT.md)

Corrección OTA candidata (#115): el System Updater original de 1.3.0 no puede instalar 1.4.0 por cambios en los archivos permitidos. Un aborto previo al reemplazo no es una instalación parcial. Conserva el registro; no reintentes, borres el estado ni cambies las rutas. El siguiente candidato conserva los contratos de rutas y permisos de 1.3.0; la actualización y reversión en TV aún requieren pruebas coordinadas.

Corrección aún no publicada (#108/#109): con System Updater preparado, el indicador y «Actualizar todo» usan la misma comprobación de la edición. Una versión general nueva sin cambios en las versiones de los componentes no ofrece reinstalación. La instalación permanece desactivada durante la comprobación. La comprobación antigua solo se usa si falta System Updater. Falta confirmar el resultado en el televisor.

Corrección de acceso #110 del candidato: el nuevo instalador registra un permiso propio de CYTV solo para las API de configuración de Homebrew. En una instalación Root existente, ejecute `cytv enable-firmware-access --edition root`, vuelva a abrir Root Home y compruebe las actualizaciones de firmware LG. No cambia ACL de Homebrew ni la opción de bloqueo. Tras una interrupción, repita el mismo comando. `cytv disable-firmware-access --edition root` revoca el acceso sin cambiar el bloqueo. El nuevo runtime mantiene el registro tras actualizaciones completas; con uno antiguo puede ser necesario repetir el comando tras actualizar solo la aplicación. Consulte requisitos, reversión y límites en la guía de firmware.

CLI candidata: al redirigir la salida en Windows, los caracteres que no admite la codificación elegida se muestran como secuencias de escape sin provocar un fallo. UTF-8 conserva el texto localizado. Esto no confirma compatibilidad Root con BX/webOS 5.
