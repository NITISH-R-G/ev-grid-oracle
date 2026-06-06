import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock global canvas behavior required by MapView (specifically buildIconAtlas)
if (typeof document !== 'undefined') {
  const originalCreateElement = document.createElement.bind(document);
  document.createElement = function(tagName: string, options?: ElementCreationOptions) {
    if (tagName.toLowerCase() === 'canvas') {
      const canvas = originalCreateElement(tagName, options) as any;
      canvas.getContext = (contextId: string, options?: any) => {
        if (contextId === '2d') {
          return {
            clearRect: vi.fn(),
            save: vi.fn(),
            restore: vi.fn(),
            globalAlpha: 1,
            fillStyle: '',
            strokeStyle: '',
            shadowColor: '',
            shadowBlur: 0,
            lineWidth: 1,
            lineCap: '',
            lineJoin: '',
            font: '',
            textAlign: '',
            textBaseline: '',
            fillRect: vi.fn(),
            fillText: vi.fn(),
            beginPath: vi.fn(),
            closePath: vi.fn(),
            moveTo: vi.fn(),
            lineTo: vi.fn(),
            arc: vi.fn(),
            arcTo: vi.fn(),
            bezierCurveTo: vi.fn(),
            stroke: vi.fn(),
            fill: vi.fn(),
          };
        }
        return null;
      };
      return canvas;
    }
    return originalCreateElement(tagName, options);
  };
}

// Global scope mocks for internal maplibre/deck functions to verify
const mockFitBounds = vi.fn();
const mockSetProps = vi.fn();

// Ensure mock dependencies are established BEFORE MapView is imported
vi.mock("maplibre-gl", () => {
  class Map {
    constructor() {
      // Mock properties
    }
    on = vi.fn()
    easeTo = vi.fn()
    addControl = vi.fn()
    fitBounds = mockFitBounds
    getCanvas = vi.fn().mockReturnValue({ setAttribute: vi.fn() })
  }

  class NavigationControl {}

  return {
    default: {
      Map,
      NavigationControl
    },
  };
});

vi.mock("@deck.gl/mapbox", () => {
  class MapboxOverlay {
    constructor() {}
    setProps = mockSetProps
  }
  return {
    MapboxOverlay
  };
});

vi.mock("@deck.gl/layers", () => {
  return {
    PathLayer: class {},
    IconLayer: class {},
    ScatterplotLayer: class {},
  };
});

// Import MapView after mocks
import { MapView } from "../MapView";

describe("MapView", () => {
  let mountEl: HTMLElement;

  beforeEach(() => {
    vi.clearAllMocks();
    mockFitBounds.mockClear();
    mockSetProps.mockClear();

    mountEl = document.createElement("div");
    document.body.appendChild(mountEl);

    // Prevent requestAnimationFrame from looping infinitely in tests
    vi.spyOn(window, "requestAnimationFrame").mockImplementation((cb) => {
      return 1 as any;
    });
  });

  it("should initialize correctly with a given element", () => {
    const mapView = new MapView(mountEl);

    // Mount element is set up correctly
    expect(mountEl.style.position).toBe("relative");
    expect(mountEl.children.length).toBe(1);

    // Verify public methods exist
    expect(typeof mapView.setSide).toBe("function");
    expect(typeof mapView.setFollowVehicle).toBe("function");
    expect(typeof mapView.bindSession).toBe("function");
    expect(typeof mapView.playExternalEvent).toBe("function");
    expect(typeof mapView.destroy).toBe("function");
  });

  it("should handle setting the side properly", () => {
    const mapView = new MapView(mountEl);

    // Check that it doesn't throw when side is changed
    expect(() => mapView.setSide("baseline")).not.toThrow();

    // Check internal state using any to bypass private
    expect((mapView as any).side).toBe("baseline");

    expect(() => mapView.setSide("oracle")).not.toThrow();
    expect((mapView as any).side).toBe("oracle");
  });

  it("should set follow vehicle property", () => {
    const mapView = new MapView(mountEl);

    mapView.setFollowVehicle(true);
    expect((mapView as any).follow).toBe(true);

    mapView.setFollowVehicle(false);
    expect((mapView as any).follow).toBe(false);
  });

  it("should bind session with stations and adjust bounds", async () => {
    const mapView = new MapView(mountEl);

    // Create some dummy stations
    const stations = [
      { station_id: "s1", lat: 12.9, lng: 77.5, total_slots: 10 },
      { station_id: "s2", lat: 13.0, lng: 77.6, total_slots: 15 }
    ];

    // Global fetch mock to handle the static road fetching
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ features: [] })
    });

    await mapView.bindSession("test-session", stations);

    // Check Map.fitBounds is called with the calculated bounds
    expect(mockFitBounds).toHaveBeenCalled();
    expect((mapView as any).stations).toEqual(stations);

    // Verify roads are set up when the fetch returns
    expect(global.fetch).toHaveBeenCalled();
  });

  it("should process an external event correctly", async () => {
    const mapView = new MapView(mountEl);

    const dummyEvent = {
      type: "route",
      ev_id: "v1",
      persona: "car",
      polyline: [[12.9, 77.5], [13.0, 77.6]],
    };

    await mapView.playExternalEvent(dummyEvent);

    // Verify the vehicle is successfully added to the internal vehicles map
    const vehicles = (mapView as any).vehicles;
    expect(vehicles.size).toBe(1);
    expect(vehicles.get("v1")).toBeDefined();
    expect(vehicles.get("v1").id).toBe("v1");
    // the ensureLngLat method flips [lat, lng] to [lng, lat]
    expect(vehicles.get("v1").route[0][0]).toEqual(dummyEvent.polyline[0][1]);
  });

  it("should properly destroy resources", () => {
    const mapView = new MapView(mountEl);
    expect(() => mapView.destroy()).not.toThrow();
  });
});
