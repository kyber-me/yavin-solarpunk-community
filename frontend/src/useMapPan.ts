import { useCallback, useEffect, useRef, useState, type DragEvent, type KeyboardEvent, type MouseEvent, type PointerEvent } from 'react';

type Position = { x: number; y: number };
type Gesture = { id: number; start: Position; last: Position; moved: boolean };
const MIN_ZOOM = .65;
const MAX_ZOOM = 1;

export function useMapPan() {
  const viewportRef = useRef<HTMLDivElement>(null);
  const position = useRef<Position>({ x: 0, y: 0 });
  const gesture = useRef<Gesture | null>(null);
  const suppressClickUntil = useRef(0);
  const [pan, setPan] = useState(position.current);
  const [dragging, setDragging] = useState(false);
  const [pressed, setPressed] = useState(false);
  const [grabPoint, setGrabPoint] = useState<Position>({ x: 0, y: 0 });
  const zoomRef = useRef(MAX_ZOOM);
  const [zoom, setZoom] = useState(MAX_ZOOM);

  const move = useCallback((next: Position) => {
    const viewport = viewportRef.current;
    if (!viewport || !viewport.clientWidth || !viewport.clientHeight) return;
    const limitX = Math.min(100, viewport.clientWidth * .08);
    const limitY = Math.min(64, viewport.clientHeight * .08);
    const bounded = {
      x: Math.max(-limitX, Math.min(limitX, next.x)),
      y: Math.max(-limitY, Math.min(limitY, next.y)),
    };
    position.current = bounded;
    setPan(bounded);
  }, []);

  const changeZoom = useCallback((next: number, anchor: Position = { x: 0, y: 0 }) => {
    const bounded = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, next));
    if (bounded === zoomRef.current) return;
    const ratio = bounded / zoomRef.current;
    zoomRef.current = bounded;
    setZoom(bounded);
    move({
      x: anchor.x - (anchor.x - position.current.x) * ratio,
      y: anchor.y - (anchor.y - position.current.y) * ratio,
    });
  }, [move]);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const preventSelection = (event: Event) => event.preventDefault();
    function wheel(event: WheelEvent) {
      event.preventDefault();
      if (gesture.current) return;
      const bounds = viewport!.getBoundingClientRect();
      const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? bounds.height : 1;
      const delta = Math.max(-300, Math.min(300, event.deltaY * unit));
      changeZoom(zoomRef.current * Math.exp(-delta * .0015), {
        x: event.clientX - bounds.left - bounds.width / 2,
        y: event.clientY - bounds.top - bounds.height / 2,
      });
    }
    viewport.addEventListener('wheel', wheel, { passive: false });
    viewport.addEventListener('selectstart', preventSelection);
    return () => {
      viewport.removeEventListener('wheel', wheel);
      viewport.removeEventListener('selectstart', preventSelection);
    };
  }, [changeZoom]);

  const finish = useCallback((pointerId?: number) => {
    const current = gesture.current;
    if (!current || (pointerId !== undefined && pointerId !== current.id)) return;
    if (current.moved) suppressClickUntil.current = performance.now() + 500;
    gesture.current = null;
    setDragging(false);
    setPressed(false);
    const viewport = viewportRef.current;
    if (viewport?.hasPointerCapture(current.id)) viewport.releasePointerCapture(current.id);
  }, []);

  useEffect(() => {
    const observer = new ResizeObserver(() => move(position.current));
    if (viewportRef.current) observer.observe(viewportRef.current);
    return () => observer.disconnect();
  }, [move]);

  useEffect(() => {
    const releasePointer = (event: globalThis.PointerEvent) => finish(event.pointerId);
    const releaseAll = () => finish();
    window.addEventListener('pointerup', releasePointer);
    window.addEventListener('pointercancel', releasePointer);
    window.addEventListener('blur', releaseAll);
    return () => {
      window.removeEventListener('pointerup', releasePointer);
      window.removeEventListener('pointercancel', releasePointer);
      window.removeEventListener('blur', releaseAll);
    };
  }, [finish]);

  function updateGrabPoint(event: PointerEvent<HTMLDivElement>) {
    const bounds = event.currentTarget.getBoundingClientRect();
    setGrabPoint({ x: event.clientX - bounds.left, y: event.clientY - bounds.top });
  }

  function onPointerDown(event: PointerEvent<HTMLDivElement>) {
    if (!event.isPrimary || event.button !== 0 || (event.target as Element).closest('button')) return;
    suppressClickUntil.current = 0;
    const selection = window.getSelection();
    if (selection && (event.currentTarget.contains(selection.anchorNode) || event.currentTarget.contains(selection.focusNode))) {
      selection.removeAllRanges();
    }
    setPressed(true);
    updateGrabPoint(event);
    gesture.current = {
      id: event.pointerId,
      start: { x: event.clientX, y: event.clientY },
      last: { x: event.clientX, y: event.clientY },
      moved: false,
    };
  }

  function onPointerMove(event: PointerEvent<HTMLDivElement>) {
    const current = gesture.current;
    if (!current || current.id !== event.pointerId) return;
    if (event.pointerType === 'mouse' && !(event.buttons & 1)) {
      finishGesture(event);
      return;
    }
    updateGrabPoint(event);
    const distance = Math.hypot(event.clientX - current.start.x, event.clientY - current.start.y);
    if (!current.moved && distance < 6) return;
    if (!current.moved) {
      current.moved = true;
      event.currentTarget.setPointerCapture(event.pointerId);
      event.currentTarget.focus({ preventScroll: true });
      setDragging(true);
    }
    // Incremental deltas let reversing respond immediately, even after hitting a limit.
    const dx = event.clientX - current.last.x;
    const dy = event.clientY - current.last.y;
    current.last = { x: event.clientX, y: event.clientY };
    move({ x: position.current.x + dx, y: position.current.y + dy });
  }

  function finishGesture(event: PointerEvent<HTMLDivElement>) {
    finish(event.pointerId);
  }

  function onPointerLeave(event: PointerEvent<HTMLDivElement>) {
    if (!gesture.current?.moved) finishGesture(event);
  }

  function onClickCapture(event: MouseEvent<HTMLDivElement>) {
    if ((event.target as Element).closest('button')) return;
    if (event.detail > 0 && performance.now() < suppressClickUntil.current) {
      event.preventDefault();
      event.stopPropagation();
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'a') {
      event.preventDefault();
      return;
    }
    if (event.target !== event.currentTarget || event.altKey || event.ctrlKey || event.metaKey) return;
    const step = event.shiftKey ? 32 : 16;
    const directions: Record<string, Position> = {
      ArrowLeft: { x: -step, y: 0 }, ArrowRight: { x: step, y: 0 },
      ArrowUp: { x: 0, y: -step }, ArrowDown: { x: 0, y: step },
    };
    if (event.key === 'Escape') {
      finish();
    } else if (['+', '=', '-', '_'].includes(event.key)) {
      event.preventDefault();
      changeZoom(zoomRef.current + (['+', '='].includes(event.key) ? .1 : -.1));
    } else if (event.key === 'Home') {
      event.preventDefault();
      move({ x: 0, y: 0 });
    } else if (directions[event.key]) {
      event.preventDefault();
      move({ x: position.current.x + directions[event.key].x, y: position.current.y + directions[event.key].y });
    }
  }

  return {
    viewportRef, pan, dragging, pressed, grabPoint, zoom,
    minZoom: MIN_ZOOM, maxZoom: MAX_ZOOM,
    setZoom: changeZoom,
    zoomIn: () => changeZoom(Math.round((zoomRef.current + .1) * 100) / 100),
    zoomOut: () => changeZoom(Math.round((zoomRef.current - .1) * 100) / 100),
    reset: () => move({ x: 0, y: 0 }),
    handlers: {
      onPointerDown, onPointerMove, onPointerUp: finishGesture,
      onPointerCancel: finishGesture, onLostPointerCapture: finishGesture,
      onClickCapture, onKeyDown, onPointerLeave,
      onDragStart: (event: DragEvent<HTMLDivElement>) => event.preventDefault(),
      onMouseDown: (event: MouseEvent<HTMLDivElement>) => {
        if (event.button === 0 && !(event.target as Element).closest('button')) event.preventDefault();
      },
    },
  };
}
