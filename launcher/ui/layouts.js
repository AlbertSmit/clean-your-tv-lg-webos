export function layoutFor(appearance, configuredColumns) {
  const tvos = appearance === 'tvos';
  const columns = tvos ? 6 : Math.max(1, Math.min(8, configuredColumns || 4));
  return {
    tvos, columns, grid: false,
    cardWidth: tvos ? 250 : 360,
    cardHeight: tvos ? 150 : 202,
    columnWidth: tvos ? 298 : 1696 / columns,
    left: tvos ? 90 : 112,
    tileBase: tvos ? 822 : 708,
    rowPitch: tvos ? 260 : 292,
    rowGap: tvos ? 0 : 36,
    dockTop: tvos ? 784 : 680,
    dockHeight: tvos ? 230 : 258,
    heroOffset: 176,
    focusScale: tvos ? 1.2 : 1.1,
    glassPadding: 24
  };
}

export function positionFor(layout, index) {
  const row = Math.floor(index / layout.columns);
  return {
    row,
    left: layout.left + index % layout.columns * layout.columnWidth +
      (layout.tvos ? 0 : (layout.columnWidth - layout.cardWidth) / 2),
    top: layout.tvos && row
      ? layout.tileBase + 230 + (row - 1) * layout.rowPitch + (layout.grid ? 30 : 0)
      : layout.tileBase + row * layout.rowPitch + (row ? layout.rowGap : 0)
  };
}

export function scrollFor(layout, index, offset, editing) {
  const position = positionFor(layout, index);
  if (layout.tvos && !editing) {
    // The first Down lifts the dock and reveals the grid as one composition.
    return position.row ? 724 + Math.max(0, position.row - 2) * layout.rowPitch : 0;
  }
  if (!position.row && !editing) return 0;
  const bottom = editing ? 850 : 1060;
  if (position.top - offset + layout.cardHeight + 70 > bottom) {
    offset = position.top + layout.cardHeight + 70 - bottom;
  }
  if (position.top - offset - 24 < 80) offset = position.top - 104;
  return offset;
}

// Six shared dock tracks. The logo owns the upper left two tracks; widgets
// occupy named regions without entering that exclusion zone or the dock.
// upper: [ logo ][ logo ][ . ][ weather ][ nowPlaying ][ nowPlaying ]
// lower: [ clock ][  .   ][ . ][    .    ][     .      ][     .      ]
export function widgetLayoutFor() {
  const layout = layoutFor('tvos');
  const square = layout.cardWidth;
  const span = layout.columnWidth + square;
  const top = 170;
  const baseline = top + span;
  return {
    columns: layout.columns,
    columnWidth: layout.columnWidth,
    cardWidth: square,
    regions: {
      logo: { left: 88, top: 62, width: span, height: 358 },
      clock: { left: layout.left, top: baseline - square, width: square, height: square },
      weather: { left: layout.left + layout.columnWidth * 3, top, width: square, height: square },
      nowPlaying: { left: layout.left + layout.columnWidth * 4, top, width: span, height: span / 2 }
    }
  };
}
