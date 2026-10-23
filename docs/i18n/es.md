# Clean Your TV — guía de uso

## Requisitos

Esta guía cubre instalación, uso y recuperación. La selección de idioma y la aplicación de escritorio para macOS/Linux corresponden a la próxima compilación o al código que incorpora este cambio. Las descargas existentes de v0.9.0 no incluyen la nueva aplicación de escritorio. Utiliza las [publicaciones del proyecto](https://github.com/Razdva122/clean-your-tv-lg-webos/releases) cuando estén disponibles, o los artefactos de una ejecución correcta de **cytv standalone builds** con este cambio.

Enciende el televisor y conecta ambos equipos a la misma red local de confianza. Después, el ordenador puede estar apagado. La compatibilidad depende del modelo, firmware y mando; Root sigue siendo una versión preliminar con pruebas físicas pendientes.

- **No-root:** activa LG Developer Mode y Key Server. Introduce la frase de acceso que muestra el televisor y acepta en él la solicitud de emparejamiento independiente. Developer Mode debe permanecer activo: su caducidad puede eliminar aplicaciones instaladas por este método. Vigila el temporizador oficial incluso con la renovación Beta activada. La supervisión de Helper necesita la red local.
- **Root:** necesitas acceso SSH root previo. El instalador no obtiene root. No actives Developer Mode sobre una instalación ya rooteada. Conserva el acceso root y los servicios de recuperación.

## Instalación e idioma

- **Windows x64:** extrae el paquete de consola y abre `cytv.exe`. En PowerShell sustituye `./cytv` por `.\cytv.exe` en los comandos siguientes. No se incluye una aplicación gráfica para Windows.
- **macOS 13+:** extrae `cytv-macos-arm64.zip` para Apple Silicon o `cytv-macos-x64.zip` para Intel, mueve `cytv.app` a Aplicaciones y ábrela. Permite el acceso a la red local. Si se bloquea una descarga de confianza, usa Privacidad y seguridad → Abrir igualmente; no desactives Gatekeeper. La aceptación en sistemas antiguos no está confirmada.
- **Linux x64:** en Ubuntu 22.04+, Debian 12+ o Mint 21+, instala `cytv-linux-x64.deb` con el gestor gráfico de paquetes y abre Clean Your TV desde el menú de aplicaciones. Las bibliotecas pueden requerir Internet. No hay paquete Linux ARM.

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
