from chainer import cuda


def delta_encode(raw_bbox, base_raw_bbox):
    """Encode bounding boxes into offsets and scales.

    Given a bounding box, this function computes offsets and scaling to match
    the box to the ground truth box.
    Mathematcially, given a bounding whose center is :math:`p_x, p_y` and size
    :math:`p_w, p_h` and the ground truth bounding box whose center is
    :math:`g_x, g_y` and size :math:`g_w, g_h`, the regression targets
    :math:`t_x, t_y, t_w, t_h` can be computed by the following formulas.

    * :math:`t_x = \\frac{(g_x - p_x)} {p_w}`
    * :math:`t_y = \\frac{(g_y - p_y)} {p_h}`
    * :math:`t_w = \\log(\\frac{g_w} {p_w})`
    * :math:`t_h = \\log(\\frac{g_h} {p_h})`

    The output is same type as the type of the inputs.
    The encoding formulas are used in works such as R-CNN [1].

    .. [1] Ross Girshick, Jeff Donahue, Trevor Darrell, Jitendra Malik. \
    Rich feature hierarchies for accurate object detection and semantic \
    segmentation. CVPR 2014.

    Args:
        raw_bbox (array): An image coordinate array whose shape is
            :math:`(R, 4)`. :math:`R` is the number of bounding boxes.
        base_raw_bbox (array): An image coordinate array whose shape is
            :mat:`(R, 4)`.

    Returns:
        array:
        Bounding box offsets and scales from :obj:`raw_bbox` \
        to :obj:`base_raw_bbox`. \
        This has shape :math:`(R, 4)`.
        The second axis contains four values :math:`t_x, t_y, t_w, t_h`.

    """
    xp = cuda.get_array_module(raw_bbox)

    width = raw_bbox[:, 2] - raw_bbox[:, 0]
    height = raw_bbox[:, 3] - raw_bbox[:, 1]
    ctr_x = raw_bbox[:, 0] + 0.5 * width
    ctr_y = raw_bbox[:, 1] + 0.5 * height

    base_width = base_raw_bbox[:, 2] - base_raw_bbox[:, 0]
    base_height = base_raw_bbox[:, 3] - base_raw_bbox[:, 1]
    base_ctr_x = base_raw_bbox[:, 0] + 0.5 * base_width
    base_ctr_y = base_raw_bbox[:, 1] + 0.5 * base_height

    dx = (base_ctr_x - ctr_x) / width
    dy = (base_ctr_y - ctr_y) / height
    dw = xp.log(base_width / width)
    dh = xp.log(base_height / height)

    bbox = xp.vstack((dx, dy, dw, dh)).transpose()
    return bbox
