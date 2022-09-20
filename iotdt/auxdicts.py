transtypes = {
    'string': 'string',
    'integer' : 'long',
    'number': 'double', 
    'bool' : 'boolean',
    'date-time': 'datetime'
}

defvalues = {
    'string' : '""',
    'long' : 0,
    'double' : 0.0,
    'boolean' : 'false',
    'datetime' : '2022-01-01T00:00:00'
    ''
}

queries = {
    'uid_check' : """
        match
            $dev isa device, has name $ndev, has uid $uiddev; $uiddev "{}";
        get 
            $dev, $ndev, $uiddev;
    """,
    'modules_check' : """
        match
            $dev isa device, has name $ndev, has uid $uiddev; $uiddev "{}";
            $includes (device: $dev, module: $mod) isa includes;
            $mod isa module;
        get 
            $mod;
    """,
    'properties_check' : """
        match 
            $mod isa module, has {} $prop_value;
        get
            $prop_value;
    """
}

