from autodiscovery.commands.run import AbstractRunCommand
from autodiscovery.exceptions import ReportableException


class RunFromReportCommand(AbstractRunCommand):
    def execute(self, parsed_entries, cs_ip, cs_user, cs_password, additional_vendors_data):
        """

        :param list[autodiscovery.reports.base.Entry] parsed_entries:
        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :param list[dict] additional_vendors_data:
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(additional_vendors_data=additional_vendors_data)
        self._init_cs_session(cs_ip=cs_ip, cs_user=cs_user, cs_password=cs_password)

        for parsed_entry in parsed_entries:
            self.logger.info("Uploading device with IP {}".format(parsed_entry.ip))
            try:
                with self.report.edit_entry(entry=parsed_entry) as entry:

                    if entry.status == entry.SUCCESS_STATUS:
                        continue
                    else:
                        entry.status = entry.SUCCESS_STATUS

                    vendor = vendor_config.get_vendor(vendor_name=parsed_entry.vendor)

                    if vendor is None:
                        raise ReportableException("Unsupported vendor {}".format(parsed_entry.vendor))

                    try:
                        handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                    except KeyError:
                        raise ReportableException("Invalid vendor type '{}'. Possible values are: {}"
                                                  .format(vendor.vendor_type, self.vendor_type_handlers_map.keys()))

                    handler.upload(entry=entry,  vendor=vendor, cs_session=self.cs_session)

            except Exception:
                self.logger.exception("Failed to upload {} device due to:".format(parsed_entry.ip))
            else:
                self.logger.info("Device with IP {} was successfully uploaded".format(parsed_entry.ip))

        self.report.generate()
