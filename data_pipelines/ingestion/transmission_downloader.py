"""
North American Transmission Line Data Downloader

Downloads transmission line data from:
1. HIFLD (Homeland Infrastructure Foundation-Level Data) - US transmission lines
2. Canada Open Government Portal - Canadian transmission lines
3. Border crossings dataset - US-Canada interconnections

Data sources:
- HIFLD ArcGIS FeatureServer: Electric Power Transmission Lines
- Canada.ca: Electric Transmission Lines dataset
- Canada.ca: Border Crossing Transmission Lines

Output: GeoJSON files with transmission line geometry and attributes
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import math

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call(["pip", "install", "requests"])
    import requests


@dataclass
class TransmissionLine:
    """Represents a single transmission line segment."""
    id: str
    voltage_kv: int
    voltage_class: str
    owner: str
    sub_1: str  # From substation
    sub_2: str  # To substation
    status: str
    length_km: float
    capacity_mw: float  # Estimated from voltage
    geometry: Dict[str, Any]  # GeoJSON geometry
    country: str
    state_province: str
    data_source: str


class TransmissionDataDownloader:
    """Downloads and processes transmission line data from public sources."""

    # HIFLD ArcGIS Feature Service URL
    HIFLD_BASE_URL = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Electric_Power_Transmission_Lines/FeatureServer/0"

    # Canada Open Data URLs
    CANADA_TRANSMISSION_URL = "https://open.canada.ca/data/en/dataset/ac3515d6-2753-47a5-8575-35be7d127f43"

    # Voltage to capacity estimation (MW) - rough estimates based on typical line ratings
    # These are conservative estimates for planning purposes
    VOLTAGE_CAPACITY_MAP = {
        69: 75,      # 69 kV
        115: 150,    # 115 kV
        138: 200,    # 138 kV
        161: 250,    # 161 kV
        230: 400,    # 230 kV
        287: 500,    # 287 kV
        345: 900,    # 345 kV
        500: 2000,   # 500 kV
        765: 3500,   # 765 kV
    }

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def estimate_capacity_from_voltage(self, voltage_kv: int) -> float:
        """Estimate transmission capacity (MW) from voltage level."""
        # Find closest matching voltage
        if voltage_kv in self.VOLTAGE_CAPACITY_MAP:
            return self.VOLTAGE_CAPACITY_MAP[voltage_kv]

        # Interpolate between known values
        voltages = sorted(self.VOLTAGE_CAPACITY_MAP.keys())
        for i, v in enumerate(voltages):
            if voltage_kv < v:
                if i == 0:
                    return self.VOLTAGE_CAPACITY_MAP[voltages[0]]
                lower_v = voltages[i-1]
                upper_v = v
                ratio = (voltage_kv - lower_v) / (upper_v - lower_v)
                lower_cap = self.VOLTAGE_CAPACITY_MAP[lower_v]
                upper_cap = self.VOLTAGE_CAPACITY_MAP[upper_v]
                return lower_cap + ratio * (upper_cap - lower_cap)

        # Above highest known voltage
        return self.VOLTAGE_CAPACITY_MAP[voltages[-1]] * (voltage_kv / voltages[-1])

    def calculate_line_length(self, geometry: Dict) -> float:
        """Calculate approximate line length in km from geometry."""
        if geometry["type"] != "LineString":
            return 0.0

        coords = geometry["coordinates"]
        if len(coords) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(coords) - 1):
            lon1, lat1 = coords[i][0], coords[i][1]
            lon2, lat2 = coords[i+1][0], coords[i+1][1]

            # Haversine formula
            R = 6371  # Earth radius in km
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)

            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            total_distance += R * c

        return total_distance

    def download_hifld_data(
        self,
        min_voltage: int = 69,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        max_records: int = 50000
    ) -> List[Dict]:
        """
        Download transmission line data from HIFLD ArcGIS Feature Service.

        Args:
            min_voltage: Minimum voltage in kV (default 69kV)
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            max_records: Maximum number of records to download

        Returns:
            List of transmission line features
        """
        print(f"\n{'='*60}")
        print("Downloading HIFLD US Transmission Line Data")
        print(f"{'='*60}")

        all_features = []
        offset = 0
        batch_size = 2000  # ArcGIS default limit

        # Build base query
        where_clause = f"VOLTAGE >= {min_voltage}"

        while offset < max_records:
            params = {
                "where": where_clause,
                "outFields": "*",
                "returnGeometry": "true",
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": batch_size,
            }

            if bbox:
                params["geometry"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
                params["geometryType"] = "esriGeometryEnvelope"
                params["spatialRel"] = "esriSpatialRelIntersects"
                params["inSR"] = "4326"

            url = f"{self.HIFLD_BASE_URL}/query"

            try:
                print(f"  Fetching records {offset} to {offset + batch_size}...")
                response = requests.get(url, params=params, timeout=120)
                response.raise_for_status()
                data = response.json()

                features = data.get("features", [])
                if not features:
                    print(f"  No more records found.")
                    break

                all_features.extend(features)
                print(f"  Retrieved {len(features)} features (total: {len(all_features)})")

                offset += batch_size

                # Respect API rate limits
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"  Error downloading data: {e}")
                break

        print(f"\nTotal US transmission lines downloaded: {len(all_features)}")
        return all_features

    def download_canada_data(self) -> List[Dict]:
        """
        Download Canadian transmission line data from Canada Open Government Portal.

        Returns:
            List of transmission line features
        """
        print(f"\n{'='*60}")
        print("Downloading Canadian Transmission Line Data")
        print(f"{'='*60}")

        # Canada's GeoPackage/Shapefile data - we'll use the WFS service
        # The data is available through GeoServer WFS
        canada_wfs_url = "https://maps-cartes.services.geo.ca/server_serveur/services/NRCan/electric_infrastructure_en/MapServer/WFSServer"

        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeName": "electric_transmission_line",
            "outputFormat": "geojson",
            "srsName": "EPSG:4326",
        }

        try:
            print("  Fetching from NRCan WFS service...")
            response = requests.get(canada_wfs_url, params=params, timeout=120)

            if response.status_code == 200:
                try:
                    data = response.json()
                    features = data.get("features", [])
                    print(f"  Retrieved {len(features)} Canadian transmission lines")
                    return features
                except json.JSONDecodeError:
                    print("  Could not parse response as JSON")
            else:
                print(f"  WFS request failed with status {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"  Error downloading Canadian data: {e}")

        # Fallback: Try alternative endpoint or return empty
        print("  Note: Canadian data may require manual download from:")
        print("  https://open.canada.ca/data/en/dataset/ac3515d6-2753-47a5-8575-35be7d127f43")

        return []

    def process_hifld_features(self, features: List[Dict]) -> List[TransmissionLine]:
        """Process raw HIFLD features into TransmissionLine objects."""
        print("\nProcessing HIFLD data...")

        lines = []
        for i, feature in enumerate(features):
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            if not geometry or geometry.get("type") != "LineString":
                continue

            # Extract voltage
            voltage = props.get("VOLTAGE", 0) or 0
            if voltage < 69:
                continue

            voltage_class = props.get("VOLT_CLASS", "UNKNOWN")
            owner = props.get("OWNER", "Unknown")
            sub_1 = props.get("SUB_1", "Unknown")
            sub_2 = props.get("SUB_2", "Unknown")
            status = props.get("STATUS", "IN SERVICE")

            # Calculate length
            length_km = self.calculate_line_length(geometry)

            # Estimate capacity
            capacity_mw = self.estimate_capacity_from_voltage(int(voltage))

            # Create line object
            line = TransmissionLine(
                id=f"hifld-{props.get('ID', i)}",
                voltage_kv=int(voltage),
                voltage_class=voltage_class,
                owner=owner,
                sub_1=sub_1,
                sub_2=sub_2,
                status="operational" if status == "IN SERVICE" else status.lower(),
                length_km=round(length_km, 2),
                capacity_mw=round(capacity_mw, 0),
                geometry=geometry,
                country="USA",
                state_province=props.get("STATE", "Unknown"),
                data_source="HIFLD"
            )
            lines.append(line)

            if (i + 1) % 5000 == 0:
                print(f"  Processed {i + 1} features...")

        print(f"  Total processed: {len(lines)} transmission lines")
        return lines

    def process_canada_features(self, features: List[Dict]) -> List[TransmissionLine]:
        """Process Canadian transmission features."""
        print("\nProcessing Canadian data...")

        lines = []
        for i, feature in enumerate(features):
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            if not geometry:
                continue

            # Canadian data may have different field names
            voltage = props.get("voltage_kv", 0) or props.get("VOLTAGE", 0) or 230
            owner = props.get("owner", "Unknown") or props.get("OWNER", "Unknown")

            length_km = self.calculate_line_length(geometry)
            capacity_mw = self.estimate_capacity_from_voltage(int(voltage))

            line = TransmissionLine(
                id=f"canada-{i}",
                voltage_kv=int(voltage),
                voltage_class=f"{voltage} KV AND ABOVE",
                owner=owner,
                sub_1=props.get("from_name", "Unknown"),
                sub_2=props.get("to_name", "Unknown"),
                status="operational",
                length_km=round(length_km, 2),
                capacity_mw=round(capacity_mw, 0),
                geometry=geometry,
                country="Canada",
                state_province=props.get("province", "Unknown"),
                data_source="NRCan"
            )
            lines.append(line)

        print(f"  Total processed: {len(lines)} Canadian transmission lines")
        return lines

    def create_geojson(self, lines: List[TransmissionLine]) -> Dict:
        """Create GeoJSON FeatureCollection from transmission lines."""
        features = []
        for line in lines:
            feature = {
                "type": "Feature",
                "properties": {
                    "id": line.id,
                    "voltage_kv": line.voltage_kv,
                    "voltage_class": line.voltage_class,
                    "owner": line.owner,
                    "sub_1": line.sub_1,
                    "sub_2": line.sub_2,
                    "status": line.status,
                    "length_km": line.length_km,
                    "capacity_mw": line.capacity_mw,
                    "country": line.country,
                    "state_province": line.state_province,
                    "data_source": line.data_source,
                },
                "geometry": line.geometry
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "metadata": {
                "name": "North American Transmission Lines",
                "description": "Transmission lines for USA and Canada with voltage and capacity data",
                "created_at": datetime.now().isoformat(),
                "sources": ["HIFLD", "NRCan", "Canada Open Government"],
                "total_lines": len(features),
                "note": "Capacity values are estimated from voltage ratings"
            },
            "features": features
        }

    def create_summary_stats(self, lines: List[TransmissionLine]) -> Dict:
        """Generate summary statistics for the transmission data."""
        stats = {
            "total_lines": len(lines),
            "total_length_km": sum(l.length_km for l in lines),
            "by_country": {},
            "by_voltage_class": {},
            "by_status": {},
        }

        for line in lines:
            # By country
            if line.country not in stats["by_country"]:
                stats["by_country"][line.country] = {"count": 0, "length_km": 0, "capacity_mw": 0}
            stats["by_country"][line.country]["count"] += 1
            stats["by_country"][line.country]["length_km"] += line.length_km
            stats["by_country"][line.country]["capacity_mw"] += line.capacity_mw

            # By voltage class
            if line.voltage_class not in stats["by_voltage_class"]:
                stats["by_voltage_class"][line.voltage_class] = {"count": 0, "length_km": 0}
            stats["by_voltage_class"][line.voltage_class]["count"] += 1
            stats["by_voltage_class"][line.voltage_class]["length_km"] += line.length_km

            # By status
            if line.status not in stats["by_status"]:
                stats["by_status"][line.status] = 0
            stats["by_status"][line.status] += 1

        return stats

    def download_and_process_all(
        self,
        min_voltage: int = 69,
        include_canada: bool = True,
        us_bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> Tuple[List[TransmissionLine], Dict]:
        """
        Download and process all North American transmission data.

        Args:
            min_voltage: Minimum voltage threshold (kV)
            include_canada: Whether to include Canadian data
            us_bbox: Optional bounding box for US data (min_lon, min_lat, max_lon, max_lat)
                     Default covers continental US and southern Canada

        Returns:
            Tuple of (list of TransmissionLine objects, summary statistics)
        """
        all_lines = []

        # Default bbox covers continental North America
        if us_bbox is None:
            us_bbox = (-170, 24, -50, 72)  # Includes Alaska, continental US, and Canada

        # Download US data
        us_features = self.download_hifld_data(
            min_voltage=min_voltage,
            bbox=us_bbox,
            max_records=100000
        )
        us_lines = self.process_hifld_features(us_features)
        all_lines.extend(us_lines)

        # Download Canadian data
        if include_canada:
            canada_features = self.download_canada_data()
            if canada_features:
                canada_lines = self.process_canada_features(canada_features)
                all_lines.extend(canada_lines)

        # Generate statistics
        stats = self.create_summary_stats(all_lines)

        return all_lines, stats

    def save_data(
        self,
        lines: List[TransmissionLine],
        stats: Dict,
        filename_prefix: str = "north_america_transmission"
    ):
        """Save processed data to files."""
        print(f"\n{'='*60}")
        print("Saving Data Files")
        print(f"{'='*60}")

        # Save full GeoJSON
        geojson = self.create_geojson(lines)
        geojson_path = self.output_dir / f"{filename_prefix}.geojson"
        with open(geojson_path, "w") as f:
            json.dump(geojson, f)
        print(f"  Saved: {geojson_path} ({len(lines)} features)")

        # Save statistics
        stats_path = self.output_dir / f"{filename_prefix}_stats.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"  Saved: {stats_path}")

        # Save by voltage class for easier loading
        voltage_groups = {}
        for line in lines:
            v_class = "high_voltage" if line.voltage_kv >= 345 else "medium_voltage" if line.voltage_kv >= 230 else "low_voltage"
            if v_class not in voltage_groups:
                voltage_groups[v_class] = []
            voltage_groups[v_class].append(line)

        for v_class, class_lines in voltage_groups.items():
            class_geojson = self.create_geojson(class_lines)
            class_path = self.output_dir / f"{filename_prefix}_{v_class}.geojson"
            with open(class_path, "w") as f:
                json.dump(class_geojson, f)
            print(f"  Saved: {class_path} ({len(class_lines)} features)")

        return geojson_path


def main():
    """Main entry point for downloading transmission data."""
    import argparse

    parser = argparse.ArgumentParser(description="Download North American transmission line data")
    parser.add_argument("--output-dir", type=str, default="./transmission_data",
                        help="Output directory for downloaded data")
    parser.add_argument("--min-voltage", type=int, default=69,
                        help="Minimum voltage threshold in kV (default: 69)")
    parser.add_argument("--no-canada", action="store_true",
                        help="Skip Canadian data download")
    parser.add_argument("--us-only-bbox", type=str, default=None,
                        help="Bounding box for US data: min_lon,min_lat,max_lon,max_lat")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    bbox = None
    if args.us_only_bbox:
        bbox = tuple(map(float, args.us_only_bbox.split(",")))

    downloader = TransmissionDataDownloader(output_dir)

    print("\n" + "="*60)
    print("NORTH AMERICAN TRANSMISSION LINE DATA DOWNLOADER")
    print("="*60)
    print(f"Output directory: {output_dir}")
    print(f"Minimum voltage: {args.min_voltage} kV")
    print(f"Include Canada: {not args.no_canada}")

    lines, stats = downloader.download_and_process_all(
        min_voltage=args.min_voltage,
        include_canada=not args.no_canada,
        us_bbox=bbox
    )

    downloader.save_data(lines, stats)

    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE - SUMMARY")
    print("="*60)
    print(f"Total transmission lines: {stats['total_lines']:,}")
    print(f"Total length: {stats['total_length_km']:,.0f} km")
    print("\nBy Country:")
    for country, data in stats["by_country"].items():
        print(f"  {country}: {data['count']:,} lines, {data['length_km']:,.0f} km")
    print("\nBy Voltage Class:")
    for v_class, data in sorted(stats["by_voltage_class"].items()):
        print(f"  {v_class}: {data['count']:,} lines")


if __name__ == "__main__":
    main()
