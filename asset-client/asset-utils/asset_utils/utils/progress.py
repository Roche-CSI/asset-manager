import sys

from tqdm import tqdm, utils

from asset_utils.utils.log_utils import LoggingMixin, LogColors, colored_string


class Progress(tqdm, LoggingMixin):

    @classmethod
    def progress_bar(cls, total=None, desc=None, **kwargs):
        """
        Parameters
        ----------
        total: int
            total number of updates
        desc: str
            progress bar description
        kwargs: dict
            additional attributes of tqdm.tqdm
        Returns
        -------

        """
        kwargs['total'] = total
        kwargs['init_allowed'] = True
        kwargs['desc'] = desc
        # tqdm progress bar is printed in the following format
        # '{l_bar}{bar}{r_bar}'
        # l_bar = '{desc}: {percentage:3.0f}%|'
        # r_bar = '| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, ' '{rate_fmt}{postfix}]'
        # to deactivate the [00:05<00:00, 25.03it/s] logged after progress bar, uncomment the following line
        # kwargs['bar_format'] = '{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}'  # removed it/s from tqdm
        return cls(**kwargs)

    @classmethod
    def status_bar(cls, total=None, desc=None, **kwargs):
        kwargs['total'] = total
        kwargs['bar_format'] = '{desc}: ...'
        kwargs['init_allowed'] = True
        kwargs['desc'] = desc
        return cls(**kwargs)

    def __init__(self, position=0, ncols=100, leave=True, **kwargs):
        if 'init_allowed' not in kwargs:
            raise Exception(
                "private constructor, please use class-methods Progress.progress_bar or Progress.status_bar instead")
        kwargs.pop('init_allowed')  # pop it before passing data to tqdm
        kwargs['position'] = position
        kwargs['ncols'] = ncols
        kwargs['leave'] = leave
        kwargs['file'] = sys.stdout  # print to stdout
        super().__init__(**kwargs)

    def close(self, message: str = "", force: bool = False, color: LogColors = None):
        """Cleanup and (if leave=False) close the progressbar."""
        if self.disable and not force:
            return

        # Prevent multiple closures
        self.disable = True

        # decrement instance pos and remove from internal set
        pos = abs(self.pos)
        self._decr_instances(self)

        if self.last_print_t < self.start_t + self.delay:
            # haven't ever displayed; nothing to clear
            return

        # GUI mode
        if getattr(self, 'sp', None) is None:
            return

        # annoyingly, _supports_unicode isn't good enough
        def fp_write(s):
            self.fp.write(utils._unicode(s))

        try:
            fp_write('')
        except ValueError as e:
            if 'closed' in str(e):
                return
            raise  # pragma: no cover

        leave = pos == 0 if self.leave is None else self.leave

        message = colored_string(message, color=color or LogColors.PROGRESS)

        with self._lock:
            if leave:
                # stats for overall rate (no weighted average)
                self._ema_dt = lambda: None
                self.display(pos=0)
                fp_write(f' {message}\n')
            else:
                # clear previous display
                if self.display(msg='', pos=pos) and not pos:
                    fp_write(f' {message}\r')
