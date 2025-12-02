from marshmallow import Schema, fields, validate, validates, ValidationError


class ArticleCreateSchema(Schema):
    """Schema for creating an article"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    author = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(validate=validate.Length(max=50), load_default='general')
    tags = fields.List(fields.Str(), load_default=list)

    @validates('title')
    def validate_title(self, value):
        if not value.strip():
            raise ValidationError('Title cannot be empty or just whitespace')

    @validates('content')
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError('Content cannot be empty or just whitespace')

    @validates('author')
    def validate_author(self, value):
        if not value.strip():
            raise ValidationError('Author cannot be empty or just whitespace')


class ArticleUpdateSchema(Schema):
    """Schema for updating an article"""
    title = fields.Str(validate=validate.Length(min=1, max=200))
    content = fields.Str(validate=validate.Length(min=1))
    author = fields.Str(validate=validate.Length(min=1, max=100))
    category = fields.Str(validate=validate.Length(max=50))
    tags = fields.List(fields.Str())
    status = fields.Str(validate=validate.OneOf(['draft', 'published', 'archived']))


class ArticleResponseSchema(Schema):
    """Schema for article response"""
    id = fields.Int(dump_only=True)
    title = fields.Str()
    content = fields.Str()
    author = fields.Str()
    category = fields.Str()
    tags = fields.List(fields.Str())
    status = fields.Str()
    views_count = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(dump_only=True, allow_none=True)


class PageInfoSchema(Schema):
    """Schema for pagination info"""
    current_page = fields.Int()
    total_pages = fields.Int()
    per_page = fields.Int()
    total_items = fields.Int()
    has_next = fields.Bool()
    has_prev = fields.Bool()


class ArticleListSchema(Schema):
    """Schema for list of articles with pagination"""
    items = fields.List(fields.Nested(ArticleResponseSchema))
    page_info = fields.Nested(PageInfoSchema)
