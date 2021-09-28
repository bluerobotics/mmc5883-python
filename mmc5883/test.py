#!/usr/bin/python3

def main():
    from mmc5883 import MMC5883
    from llog import LLogWriter

    device = "mmc5883"
    parser = LLogWriter.create_default_parser(__file__, device)
    args = parser.parse_args()


    with llog.LLogWriter(args.meta, args.output) as log:
        mmc = MMC5883()

        def data_getter():
            data = mmc.measure()
            return f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x} {data.y} {data.z} {data.t}"

        log.log_data_loop(data_getter, parser_args=args)

if __name__ == '__main__':
    main()
