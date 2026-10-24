# Clean Your TV — guía de uso

No-root y Root son opciones equivalentes para distintas configuraciones del televisor. Elige No-root para LG Developer Mode o Root si ya tienes acceso root por SSH. La compatibilidad y las pruebas realizadas son específicas de cada edición.

## Requisitos

Esta guía cubre instalación, uso y recuperación. La selección de idioma y la aplicación de escritorio para macOS/Linux están incluidas en [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3). Las descargas antiguas de v0.9.0 no incluyen la aplicación de escritorio. Consulta la [instalación de ambas ediciones](../INSTALL.md).

Enciende el televisor y conecta ambos equipos a la misma red local de confianza. Después, el ordenador puede estar apagado. La compatibilidad depende del modelo, firmware y mando; Root tiene pruebas físicas pendientes.

- **No-root:** activa LG Developer Mode y Key Server. Introduce la frase de acceso que muestra el televisor y acepta en él la solicitud de emparejamiento independiente. Developer Mode debe permanecer activo: su caducidad puede eliminar aplicaciones instaladas por este método. Vigila el temporizador oficial incluso con la renovación Beta activada. La supervisión de Helper necesita la red local.
- **Root:** necesitas acceso SSH root previo. El instalador no obtiene root. No actives Developer Mode sobre una instalación ya rooteada. Conserva el acceso root y los servicios de recuperación.

## Instalación e idioma

- **Windows x64:** descarga `cytv-windows-x64-desktop.zip`, elige **Extraer todo** en el Explorador y abre `cytv-desktop/cytv-desktop.exe`. Conserva la carpeta `_internal` a su lado. No se ha configurado la firma de editor de Windows. La consola separada es `cytv-windows-x64.exe`; renómbrala a `cytv.exe` y usa `.\cytv.exe` en PowerShell para los comandos siguientes.
- **macOS 13+:** extrae `cytv-macos-arm64.zip` para Apple Silicon o `cytv-macos-x64.zip` para Intel, mueve `cytv.app` a Aplicaciones y ábrela. Permite el acceso a la red local. Si se bloquea una descarga de confianza, usa Privacidad y seguridad → Abrir igualmente; no desactives Gatekeeper. La aceptación en sistemas antiguos no está confirmada.
- **Linux x64:** en Ubuntu 22.04+, Debian 12+ o Mint 21+, instala `cytv-linux-x64.deb` con el gestor gráfico de paquetes y abre Clean Your TV desde el menú de aplicaciones. Las bibliotecas pueden requerir Internet. No hay paquete Linux ARM. El ejecutable independiente `cytv-linux-x64` es la CLI; usa el `.deb` para la app gráfica.

[Instalador Android](../../android/README.md): incluye los diez idiomas de la interfaz. El control superior derecho muestra el idioma actual; tócalo para elegir otro. La selección se guarda en el teléfono.

El asistente de escritorio usa inicialmente el idioma del sistema y guarda una selección explícita. En el televisor, abre **Ajustes → Idioma** y elige un idioma o la opción automática del sistema. Las preferencias del instalador y del televisor son independientes. Consulta los códigos en el [índice de idiomas](../LANGUAGES.md).

Para la CLI descargada por separado en macOS/Linux, desde la carpeta extraída:

```sh
chmod +x cytv
./cytv --language es install
```

Selecciona el televisor o introduce su IP, elige la edición y revisa el resumen. Confirma una nueva identidad SSH solo para tu televisor en una red de confianza; una clave guardada que haya cambiado bloquea el acceso. Root prepara la recuperación y activa Home inmediatamente, sin prueba temporal ni paso de conservación. Comprueba flechas, OK, Home, Atrás/Cancelar, volumen, suspensión y arranque en frío.

## Uso y recuperación

Las flechas seleccionan y OK abre; mantén OK para reordenar. Una pulsación breve de Atrás conserva la navegación y confirmación de salida de cada aplicación. Home abre el lanzador mientras el control está activo. En las nuevas compilaciones, mantén Atrás durante 1,2 segundos para abrir LG Home una vez. El interruptor de control de Home y tus ajustes no cambian.

**Compilaciones nuevas: pulsa Home tres veces en dos segundos**, soltando entre pulsaciones. Se recupera LG Home y se detiene el control sin borrar preferencias. En No-root Helper hasta 0.6.13 inclusive, mantén Home unos dos segundos. Mantener Home no es el gesto de emergencia de Root.

No-root: abre **Home Helper** desde las aplicaciones de LG para reanudar; abrir Home solo no elimina la parada. Root: activa **Cambiar Home** en los ajustes de Home para reanudar. **Abrir LG Home** lo abre una vez sin cambiar el destino de Home. Para recuperar LG Home como destino permanente, desactiva **Cambiar Home** o ejecuta `cytv restore`. No ejecutes ambos controladores a la vez. Si el fallo se repite, deja LG Home activo.

```sh
./cytv --language es status
./cytv --language es doctor --report
./cytv --language es restore
./cytv --language es uninstall
```

Tras una interrupción, ejecuta primero `status` y conserva los registros. `restore` recupera LG Home sin quitar aplicaciones; `uninstall` lo restaura antes de eliminarlas. Los datos de recuperación Root se conservan deliberadamente: no los borres para forzar otra instalación. Revisa los informes antes de compartirlos; no publiques claves ni carpetas de perfiles.

## Actualizaciones y eliminación

Guarda paquetes funcionales y copias privadas de ajustes. Detén No-root Helper antes de sustituir paquetes y actualiza desde el ordenador sin desinstalar primero: podrías perder ajustes. La instalación combinada Root de cytv incluye un actualizador para versiones compatibles en Ajustes → Actualizaciones de software; la instalación manual tiene otras limitaciones. No sobrescribas una ejecución Root activa con una IPK suelta. Utiliza el proceso explícito de reinstalación de cytv. Desinstalar la aplicación del ordenador no elimina las aplicaciones del televisor.

Documentación técnica en inglés: [escritorio](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [instalación manual](../MANUAL_INSTALL.md), [recuperación](../RECOVERY.md), [ediciones](../EDITIONS.md).

Tras conectar, cytv lee las versiones del televisor y muestra la versión actual → incluida para Home y Home Helper (No-root), o Root y Root Updater. Revise y confirme antes de instalar. Se indican las instalaciones nuevas, reinstalaciones y versiones anteriores; `--yes` omite la confirmación, pero muestra las versiones.

Actualizaciones de software muestra detalles solo de la versión instalada o una más reciente. Abre Recuperación para ver la versión guardada para restaurar o por qué no está disponible; Atrás vuelve a las actualizaciones.

No-root comprueba la ABI de la consola del TV y acepta un núcleo de 64 bits con entorno ARM32 verificado. Si falla la comprobación, adjunta el JSON de diagnóstico generado; no compartas claves ni frases de contraseña.

Las actualizaciones de Home piden confirmación antes de instalar; después el inicio se verifica automáticamente. La actualización del estado conserva el botón seleccionado con el mando.

En Root y No-root, el inicio se verifica automáticamente después de la instalación; no tienes que confirmar que todo funciona. La restauración sigue disponible tras la confirmación, sin límite de tiempo, hasta la próxima actualización. Devuelve la versión anterior de Home y los ajustes guardados antes de actualizar; los cambios posteriores pueden perderse. Aparece una advertencia antes de iniciar la restauración. Actualizar y restaurar No-root desde el televisor sigue requiriendo root y Homebrew Channel; de lo contrario, usa el instalador del ordenador.

La pantalla de actualización separa versiones, estado y novedades legibles. Arriba/Abajo desplaza las notas; Izquierda/Derecha elige las acciones fijas de abajo. Tras las comprobaciones automáticas de inicio, Root restaura el control de Home si estaba activado; No-root conserva el estado del Helper independiente. Si estaba desactivado o se desactiva de forma explícita o de emergencia, sigue desactivado.

Al abrir los ajustes de Home se buscan actualizaciones en segundo plano. Un punto naranja en Actualizaciones de software indica una versión más reciente, incluso si requiere instalación desde el ordenador. Puedes seguir usando los ajustes durante la búsqueda.

No-root: abre Ajustes de Home → Modo de desarrollador para la renovación automática, la comprobación de sesión y el diagnóstico. La pantalla principal mantiene visibles el estado resumido y los errores de renovación. Atrás vuelve a los ajustes de Home. Ambas ediciones agrupan Idioma, Actualizaciones de software y Ajustes del TV en la misma fila; la flecha abre cada opción.
