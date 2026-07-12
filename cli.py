#!/usr/bin/env python3
"""sdr-scanner CLI - SDR Security Testing Toolkit."""

import argparse
import json
import sys
import logging

from src.scanner.engine import SDREngine
from src.scanner.config import ScannerConfig
from src.scanner.models import COMMON_BANDS
from src.analyzers.spectrum import SpectrumAnalyzer
from src.analyzers.modulation import ModulationDetector
from src.analyzers.signal import SignalStrengthAnalyzer
from src.decoders.adsb import ADSBDecoder
from src.decoders.ais import AISDecoder
from src.decoders.fm import FMDecoder


def main():
    parser = argparse.ArgumentParser(
        prog="sdr-scanner",
        description="SDR Security Testing Toolkit",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    # scan
    scan_p = subparsers.add_parser("scan", help="Scan frequency band")
    scan_p.add_argument("--freq", type=float, help="Center frequency (Hz)")
    scan_p.add_argument("--freq-start", type=float, help="Start frequency")
    scan_p.add_argument("--freq-stop", type=float, help="Stop frequency")
    scan_p.add_argument("--step", type=float, help="Frequency step")
    scan_p.add_argument("--bandwidth", type=float, default=2e6)
    scan_p.add_argument("--duration", type=int, default=10)
    scan_p.add_argument("--device", default="rtlsdr")
    scan_p.add_argument("--detect", action="store_true")
    scan_p.add_argument("-f", "--format", choices=["table", "json"], default="table")
    scan_p.add_argument("-o", "--output")

    # record
    rec_p = subparsers.add_parser("record", help="Record IQ samples")
    rec_p.add_argument("--freq", type=float, required=True)
    rec_p.add_argument("--sample-rate", type=float, default=2.048e6)
    rec_p.add_argument("--duration", type=float, default=60)
    rec_p.add_argument("--output", required=True)

    # decode
    dec_p = subparsers.add_parser("decode", help="Decode signals")
    dec_p.add_argument("protocol", choices=["fm", "adsb", "ais", "pager"])
    dec_p.add_argument("--freq", type=float, required=True)
    dec_p.add_argument("--freq2", type=float)
    dec_p.add_argument("--duration", type=int, default=30)
    dec_p.add_argument("--protocol", dest="pager_proto", help="Pager protocol")

    # analyze
    ana_p = subparsers.add_parser("analyze", help="Analyze signal")
    ana_p.add_argument("--freq", type=float, required=True)
    ana_p.add_argument("--modulation", action="store_true")
    ana_p.add_argument("--rssi", action="store_true")
    ana_p.add_argument("--duration", type=int, default=10)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = ScannerConfig(device_type=getattr(args, "device", "rtlsdr"))
    engine = SDREngine(config=config)

    if args.command == "scan":
        engine.start()
        if hasattr(args, "freq_start") and args.freq_start and hasattr(args, "freq_stop") and args.freq_stop:
            signals = engine.scan_band(args.freq_start, args.freq_stop, step=getattr(args, "step", None))
            if args.format == "json":
                output = json.dumps([{"freq": s.frequency, "power": s.power_dbm} for s in signals], indent=2)
            else:
                output = f"{'Frequency':<15} {'Power (dBm)':<12} {'Modulation':<10}\n"
                output += "-" * 40 + "\n"
                for s in signals:
                    output += f"{s.frequency/1e6:<15.3f} {s.power_dbm:<12.1f} {s.modulation.value:<10}\n"
            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
                print(f"Results saved to {args.output}")
            else:
                print(output)
        elif args.freq:
            sample = engine.capture(frequency=args.freq, duration=1)
            spectrum = SpectrumAnalyzer()
            freqs, power = spectrum.analyze(sample)
            print(f"Captured at {args.freq/1e6:.3f} MHz")
            if args.detect:
                signals = spectrum.detect_peaks(freqs, power)
                print(f"Detected {len(signals)} signals")
        engine.stop()

    elif args.command == "record":
        engine.start()
        path = engine.record(args.output, frequency=args.freq, duration=args.duration)
        print(f"Recorded to {path}")
        engine.stop()

    elif args.command == "decode":
        engine.start()
        sample = engine.capture(frequency=args.freq, duration=args.duration)
        if args.protocol == "fm":
            decoder = FMDecoder()
            audio = decoder.demodulate(sample)
            print(f"FM decoded {len(audio)} audio samples")
        elif args.protocol == "adsb":
            decoder = ADSBDecoder()
            messages = decoder.decode(sample)
            print(f"ADS-B: {len(messages)} messages decoded")
        elif args.protocol == "ais":
            decoder = AISDecoder()
            messages = decoder.decode(sample)
            print(f"AIS: {len(messages)} messages decoded")
        engine.stop()

    elif args.command == "analyze":
        engine.start()
        sample = engine.capture(frequency=args.freq, duration=args.duration)
        if args.modulation:
            detector = ModulationDetector()
            mod = detector.detect(sample)
            quality = detector.analyze_signal_quality(sample)
            print(f"Modulation: {mod.value}")
            print(f"SNR: {quality['snr_db']:.1f} dB")
            print(f"Freq offset: {quality['frequency_offset']:.0f} Hz")
        if args.rssi:
            analyzer = SignalStrengthAnalyzer()
            power = analyzer.measure(sample)
            print(f"Power: {power:.1f} dBm")
        engine.stop()


if __name__ == "__main__":
    main()
