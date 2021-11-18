#!/usr/bin/python3

def main():
    from mmc5883 import MMC5883
    from llog import LLogWriter

    device = "mmc5883"
    parser = LLogWriter.create_default_parser(__file__, device)
    parser.add_argument("--bus", type=int, default=6, help="i2c bus")
    args = parser.parse_args()


    with LLogWriter(args.meta, args.output, console=args.console) as log:
        mmc = MMC5883(args.bus)

        def data_getter():
            data = mmc.measure()
            return f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x} {data.y} {data.z} {data.t}"

        log.log_data_loop(data_getter, parser_args=args)

if __name__ == '__main__':
    main()
