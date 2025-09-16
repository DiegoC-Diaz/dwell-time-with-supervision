'use client';

import { useState, useEffect } from 'react';
import { ChevronDown, MapPin } from 'lucide-react';
import { ZoneFilter } from '@/types/metrics';

interface ZoneFilterDropdownProps {
  selectedZoneId?: number;
  onZoneChange: (zoneId?: number) => void;
}

export function ZoneFilterDropdown({ selectedZoneId, onZoneChange }: ZoneFilterDropdownProps) {
  const [zones, setZones] = useState<ZoneFilter[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const fetchZones = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/zones');
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            const zoneFilters: ZoneFilter[] = data.zones.map((zone: any) => ({
              id: zone.id,
              name: zone.zone_name
            }));
            setZones(zoneFilters);
          }
        }
      } catch (error) {
        console.error('Error fetching zones:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, []);

  const selectedZone = zones.find(zone => zone.id === selectedZoneId);

  const handleZoneSelect = (zoneId?: number) => {
    onZoneChange(zoneId);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors border border-gray-300"
        disabled={loading}
      >
        <MapPin className="h-4 w-4" />
        <span>
          {loading ? 'Cargando...' : selectedZone ? selectedZone.name : 'Todas las zonas'}
        </span>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="py-1">
            <button
              onClick={() => handleZoneSelect(undefined)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 ${
                !selectedZoneId ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
              }`}
            >
              Todas las zonas
            </button>
            {zones.map((zone) => (
              <button
                key={zone.id}
                onClick={() => handleZoneSelect(zone.id)}
                className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 ${
                  selectedZoneId === zone.id ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                }`}
              >
                {zone.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Overlay para cerrar el dropdown */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
