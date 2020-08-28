class GroupwiseMixIn:

    def __init__(self, estimator, data, group_columns):
        groupby_obj = data.groupby(group_columns)
        self.forecasters = {grp: copy.deepcopy(
            forecaster) for grp, _ in groupby_obj}
        self.group_columns = group_columns
        return

    def __getitem__(self, item):
        try:
            return self.forecasters[item]
        except KeyError:
            if type(item) == int:
                return (list(self.forecasters)[item], self.forecasters[list(self.forecasters)[item]])
            else:
                raise

    def _apply(self, method, data=None, data_proc=None, error_handler='warn', proc_args={}, **kwargs):
        '''
        data_proc is a function that processes the input df and outputs a dictinoary containing the pieces
        of input extracted from the df
        '''
        if not data is None:
            groupby_obj = data.groupby(self.group_columns)
            return_dict = {}
            for grp, df in tqdm(groupby_obj):
                try:
                    method_inputs = data_proc(df, **proc_args)
                    assert isinstance(method_inputs, dict)
                    return_dict[grp] = getattr(self[grp], method)(
                        **method_inputs, **kwargs)
                except Exception as exc:
                    if error_handler == 'coerce':
                        pass
                    elif error_handler == 'warn':
                        print(f'Error with group {grp}: {repr(exc)}')
                    else:
                        raise
        else:
            return_dict = {}
            for grp, obj in tqdm(self.forecasters.items()):
                try:
                    return_dict[grp] = getattr(self[grp], method)(**proc_args, **kwargs)
                except Exception as exc:
                    if error_handler == 'coerce':
                        pass
                    elif error_handler == 'warn':
                        print(f'Error with group {grp}: {repr(exc)}')
                    else:
                        raise

        return return_dict
