from gendiff.generate_diff import ADDED, DELETED, NESTED, CHANGED, UNMODIFIED

SPACE = 4
OLD_VAL, NEW_VAL = 0, 1

SIGN_CONVERTER = {
    NESTED: None,
    UNMODIFIED: None,
    ADDED: '+',
    DELETED: '-'
}


def formatter(type, value, spaces, sign=None):
    left_indent = '' + (' ' * spaces)
    if not sign:
        sign = ' '
    output = '{0}{1} {2}: {3}\n'.format(left_indent, sign, type, value)
    return output


def nest_formatter(dict_, spaces):
    # Dict destructuring to key, value variables
    key, value = next(iter(dict_.items()))

    left_indent = '' + (' ' * spaces)
    output = '{{\n{0}{1}: {2}\n{0}}}'.format(left_indent, key, value)
    return output


def render(diff_dict, spaces=2):
    # Initialize output string
    output = '{' + '\n'

    # Iterate diff_dict
    for type, node in sorted(diff_dict.items()):

        # If node type has NESTED type then we put node value in render()
        # function and call it recursively
        if node['type'] == NESTED:
            output += formatter(type,
                                render(node['values'], spaces=spaces+SPACE),
                                spaces)

        # If node has dict type but not equals CHANGED nor NESTED, that
        # means node may belong to ADDED, DELETED or UNMODIFIED type.
        # In this case we need to format node by appending spaces and
        # arithmetic sign in output string (before node type)
        elif not node['type'] == CHANGED and isinstance(node['values'], dict):
            output += formatter(type,
                                render(node['values'], spaces=spaces+SPACE),
                                spaces, sign=SIGN_CONVERTER[node['type']])

        # If node has CHANGED type, these changes could have been made
        # in three ways
        elif node['type'] == CHANGED:

            # Case 1: OLD value is dict and NEW value is not
            if isinstance(node['values'][OLD_VAL], dict) and\
                    not isinstance(node['values'][NEW_VAL], dict):
                output += formatter(type, nest_formatter(
                                            node['values'][OLD_VAL],
                                            spaces=spaces+SPACE
                                            ),
                                    spaces=spaces, sign='-')
                output += formatter(type, node['values'][NEW_VAL],
                                    spaces=spaces, sign='+')

            # Case 2: NEW value is dict and OLD value is not
            elif not isinstance(node['values'][OLD_VAL], dict) and\
                    isinstance(node['values'][NEW_VAL], dict):
                output += formatter(type, nest_formatter(
                                            node['values'][NEW_VAL],
                                            spaces=spaces+SPACE
                                            ),
                                    spaces=spaces, sign='-')
                output += formatter(type, node['values'][NEW_VAL],
                                    spaces=spaces, sign='+')

            # Case 3: Both NEW & OLD values are not dict's
            else:
                output += formatter(type, node['values'][OLD_VAL],
                                    spaces=spaces, sign='+')
                output += formatter(type, node['values'][NEW_VAL],
                                    spaces=spaces, sign='-')

        # Any other cases (if node has been ADDED, DELETED or UNMODIFIED)
        else:
            output += formatter(type, node['values'],
                                spaces=spaces,
                                sign=SIGN_CONVERTER[node['type']])

    # Returning output
    output += ' ' * (spaces-2) + '}'
    return output