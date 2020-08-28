from functools import partial
class GroupwiseMixIn:

    def __init__(self, estimator, df, group_columns):
        '''
        init saves states of group instances, group columns and will create a dictinoary of estimators
        to create new estimators in the dict, you need to create a new instance of GroupwiseMixIn
        '''
        groupby_obj = df.groupby(group_columns)
        self.estimators = {grp: copy.deepcopy(
            estimator) for grp, _ in groupby_obj}
        self.group_columns = group_columns
        self.base_estimator = copy.deepcopy(estimator)
        return

    def __getitem__(self, item):
        '''
        used for retrieving estimators for each group
        '''
        try:
            return self.estimators[item]
        except KeyError:
            if type(item) == int:
                return (list(self.estimators)[item], self.estimators[list(self.estimators)[item]])
            else:
                raise

    def __getattr__(self,item):
        '''used for calling estimator methods for all groups'''
        return partial(self._apply,method = item)

    def _apply(self, df=None, group_data_proc=None, error_handler='warn',method = None, proc_args={}, **kwargs):
        '''
        group_data_proc is a function that processes the input df (for each group) and outputs a dictinoary containing the pieces
        of input extracted from the df. the keys of the dictinoary should be the inputs for the called method
        '''
        if not df is None:
            groupby_obj = df.groupby(self.group_columns)
            return_dict = {}
            for grp, df in tqdm(groupby_obj):
                try:
                    method_inputs = group_data_proc(df, **proc_args)
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
            for grp, obj in tqdm(self.estimators.items()):
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