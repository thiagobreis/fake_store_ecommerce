import pyarrow as pa

CARTS = pa.schema([
    ('id',pa.int64()),
    ('userId',pa.int64()),
    ('date',pa.timestamp('ms')),
    ('products',pa.list_(pa.struct([
        ('productId',pa.int64()),
        ('quantity',pa.int64())        
    ])))
])


USERS = pa.schema([
    ('id',pa.int64()),
    ('email',pa.string()),
    ('username',pa.string()),
    ('password',pa.string()),
    ('name',pa.struct([
        ('firstname',pa.string()),
        ('lastname',pa.string())
        ])),
    ('phone',pa.string()),
    ('address',pa.struct([
        ('geolocation',pa.struct([
            ('lat',pa.float64()),
            ('long',pa.float64())
        ])),
        ('city',pa.string()),
        ('street',pa.string()),
        ('number',pa.string()),
        ('zipcode',pa.string())
    ]))
])


PRODUCTS = pa.schema([
    ('id',pa.int64()),
    ('title',pa.string()),
    ('price',pa.float64()),
    ('description',pa.string()),
    ('category',pa.string()),
    ('image',pa.string()),
    ('rating',pa.struct([
        ('rate',pa.float64()),
        ('count',pa.int64())
        ]))
])